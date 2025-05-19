from scrapy.spiders import Spider
from scrapy.http import Request, Response, TextResponse
from urllib.parse import urlparse, urlunparse
from datetime import datetime, timezone
from typing import Generator, cast
from scrapy import signals
import json
import os
from toy_catalogue.spiders.rule_factory import SpiderConfig
from config.config import DATA_ROOT
import imghdr
import random


def canonicalise_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query=""))


def is_valid_image(image_data):
    img_type = imghdr.what(None, h=image_data)
    return img_type in ["jpeg", "png", "gif", "bmp", "webp"]


def create_spider(config: SpiderConfig) -> type[Spider]:
    class GenericSpider(Spider):
        name = config["site"]
        start_urls = config["start_urls"]
        allowed_domains = [urlparse(url).netloc for url in start_urls]
        custom_settings = {
            # "JOBDIR": f"crawls/{config['site']}",
            **config["playwright"],
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.seen_urls = set()
            self.checkpoint_data = {}

            # silence_scrapy_logs()

        @classmethod
        def from_crawler(cls, crawler, *args, **kwargs):
            # Pull param from crawler settings if needed
            spider = super().from_crawler(crawler, *args, **kwargs)
            spider.logger.info("from_crawler called")
            crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
            return spider

        async def start(self):
            # if hasattr(self, "state") and "checkpoint" in self.state:
            #     self.logger.info("Resuming from checkpoint...")
            #     self.checkpoint_data = self.state["checkpoint"]
            #     yield Request(
            #         self.checkpoint_data["last_collection_page"],
            #         callback=self.parse_collection,
            #         meta={**config["pagination_meta"]},
            #     )
            # else:
            self.logger.info("Starting fresh crawl...")
            for url in self.start_urls:
                yield Request(
                    url,
                    callback=self.parse_collection,
                    meta={**config["pagination_meta"]},
                )

        def parse(self, response):
            self.logger.warning(
                "Default parse() called. You may have forgotten to set callback."
            )

        def parse_collection(
            self, response: Response
        ) -> Generator[Request, None, None]:
            if self.is_bad_response(response) or not self._is_webpage(response):
                yield self.retry_request(response)
                return

            self.logger.info(f"Currently on Page {response.url}")
            response = cast(TextResponse, response)

            product_links = self._should_follow(config["product_strategy"](response))
            random.shuffle(product_links)
            yield from response.follow_all(
                product_links,
                callback=self.parse_product,
                priority=50,
                meta={**config["product_meta"]},
            )

            next_page = config["pagination_strategy"](response)
            if next_page:
                self.logger.info(f"Next page is {next_page}")
                yield response.follow(
                    next_page,
                    callback=self.parse_collection,
                    meta={**config["pagination_meta"]},
                )
                self.checkpoint_data["last_collection_page"] = str(response.url)

        def parse_product(self, response: Response) -> Generator[Request, None, None]:
            if self.is_bad_response(response) or not self._is_webpage(response):
                yield self.retry_request(response)
                return

            response = cast(TextResponse, response)
            try:
                # Create folder for domain
                page_id = urlparse(response.url).path.replace("/", "_").lstrip("_")
                folder_path = os.path.join(DATA_ROOT, config["site"], page_id)
                os.makedirs(folder_path, exist_ok=True)

                # Save the HTML content as a file
                with open(os.path.join(folder_path, "page.html"), "wb") as f:
                    f.write(response.body)
                metadata = {
                    "url": response.url,
                    "title": response.css("title::text").get(default="").strip(),
                    "time": datetime.now(timezone.utc).isoformat(),
                    "encoding": response.encoding,
                }
                meta_path = os.path.join(folder_path, "metadata.json")
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2)
                self.logger.info(f"Saved HTML for {response.url}")

                image_urls = response.css(f"{config['image_format']}").getall()
                image_links = self._should_follow(
                    [response.urljoin(url) for url in image_urls]
                )
                random.shuffle(image_links)
                for i, img_url in enumerate(image_links):
                    # self.logger.debug(f"Found image {img_url}")
                    yield Request(
                        url=img_url,
                        callback=self.save_image,
                        meta={"folder_path": folder_path, "index": i},
                        priority=1000,
                        dont_filter=True,
                    )
                self.checkpoint_data["last_product"] = str(response.url)
            except Exception as e:
                self.logger.error(f"Error in parse_product: {e}")
                return

        def save_image(self, response):
            if not is_valid_image(response.body):
                yield self.retry_request(response)
            path = response.meta["folder_path"]
            index = response.meta["index"]
            ext = os.path.splitext(urlparse(response.url).path)[-1] or ".jpg"
            self.logger.debug(
                f"Saved Image for {response.url} under {path} as image_{index}"
            )
            os.makedirs(os.path.join(path, "images"), exist_ok=True)
            with open(os.path.join(path, "images", f"image_{index}{ext}"), "wb") as f:
                f.write(response.body)

        def errback_retry(self, failure):
            request = failure.request
            self.logger.warning(f"Request failed: {failure.value}")
            yield self.retry_request(request)

        def retry_request(self, response_or_request):
            if isinstance(response_or_request, Request):
                request = response_or_request
            else:
                request = response_or_request.request

            return request.replace(dont_filter=True)

        def is_bad_response(self, response):
            # Check for Cloudflare captcha, login redirect, etc.
            result = (
                response.status != 200
                or b"remote_addr" in response.body.lower()
                and b"http_user-agent" in response.body.lower()
            )
            if result:
                self.logger.info("Bad Response SSL")
            return result

        def _is_webpage(self, response: Response):
            return isinstance(response, TextResponse)

        def _should_follow(self, urls: list[str]) -> list[str]:
            result = []
            for link in urls:
                url = canonicalise_url(link)
                if url not in self.seen_urls:
                    self.seen_urls.add(url)
                    result.append(url)
            return result

        def spider_closed(self, spider):
            # This will be called when the spider is closed
            self.state["checkpoint"] = self.checkpoint_data
            self.logger.info("Spider closed: %s", spider.name)
            directory = f"data/{config['site']}"
            if os.path.isdir(directory):
                folder_count = sum(
                    os.path.isdir(os.path.join(directory, entry))
                    for entry in os.listdir(directory)
                )

                self.logger.info(f"Scraped {folder_count} products")
                # shutil.rmtree(f"data/{self.name}")

    return GenericSpider
