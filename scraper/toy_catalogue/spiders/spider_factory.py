from scrapy.spiders import CrawlSpider
from scrapy.http import Request, Response, TextResponse
from urllib.parse import urlparse, urlunparse
from datetime import datetime, timezone
from typing import Generator, cast
from scrapy import signals
from urllib.parse import urljoin
import json
import os
from toy_catalogue.proxies.proxy_manager import ProxyManager


# import shutil
from toy_catalogue.settings import silence_scrapy_logs
from toy_catalogue.spiders.rule_factory import SpiderConfig
from config.config import DATA_ROOT


def canonicalise_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query=""))


def create_spider(input_rules: SpiderConfig) -> type[CrawlSpider]:
    class GenericSpider(CrawlSpider):
        name = input_rules["name"]
        start_urls = [input_rules["start_url"]]
        allowed_domains = [urlparse(url).netloc for url in start_urls]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.name = input_rules["name"]
            self.collection_le = input_rules["collection_le"]
            self.page_le = input_rules["page_le"]
            self.seen_images = set()
            silence_scrapy_logs()

        @classmethod
        def from_crawler(cls, crawler, *args, **kwargs):
            # Pull param from crawler settings if needed
            spider = super().from_crawler(crawler, *args, **kwargs)
            crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
            return spider

        def start_requests(self):
            for url in self.start_urls:
                # Explicitly tell Scrapy to use parse_collection
                yield Request(url, callback=self.parse_collection)

        def parse_collection(
            self, response: Response
        ) -> Generator[Request, None, None]:
            if self.is_bad_response(response):
                yield self.retry_request(response)
                return
            response = cast(TextResponse, response)
            link_urls = [link.url for link in self.page_le.extract_links(response)]
            yield from response.follow_all(link_urls, callback=self.parse_item)

            coll_urls = [
                link.url for link in self.collection_le.extract_links(response)
            ]
            yield from response.follow_all(coll_urls, callback=self.parse_collection)

        def parse_item(self, response: Response) -> Generator[Request, None, None]:
            if self.is_bad_response(response) or not self._is_webpage(response):
                yield self.retry_request(response)
                return
            response = cast(TextResponse, response)
            try:
                # Create folder for domain
                page_id = urlparse(response.url).path.replace("/", "_").lstrip("_")
                folder_path = os.path.join(DATA_ROOT, self.name, page_id)
                os.makedirs(os.path.join(folder_path, "images"), exist_ok=True)

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
                self.logger.debug(f"Saved HTML for {response.url}")
                image_urls = response.css("img::attr(src)").getall()
                for i, img_url in enumerate(image_urls):
                    canonical = canonicalise_url(img_url)
                    if canonical not in self.seen_images:
                        self.seen_images.add(canonical)
                        yield Request(
                            url=urljoin(response.url, img_url),
                            callback=self.save_image,
                            meta={"folder_path": folder_path, "index": i},
                        )
            except Exception as e:
                self.logger.error(f"Error in parse_item: {e}")
                return

        def save_image(self, response):
            path = response.meta["folder_path"]
            index = response.meta["index"]
            ext = os.path.splitext(urlparse(response.url).path)[-1] or ".jpg"

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

            retry_count = request.meta.get("retry_count", 0) + 1
            if retry_count > 20:
                self.logger.warning("Max retries exceeded")
                return

            new_meta = request.meta.copy()
            new_meta["retry_count"] = retry_count
            ProxyManager().mark_failure(request.meta.get("proxy"))
            if retry_count > 3:
                new_meta[
                    "proxy"
                ] = ProxyManager().get_url()  # Optional: get a new proxy
            proxy_count = 0
            for proxy in ProxyManager().proxies:
                proxy_count += int(ProxyManager().proxies[proxy].is_working)
            return request.replace(dont_filter=True, meta=new_meta)

        def is_bad_response(self, response):
            # Check for Cloudflare captcha, login redirect, etc.
            result = (
                response.status != 200
                or b"remote_addr" in response.body.lower()
                and b"http_user-agent" in response.body.lower()
            )
            if result:
                self.logger.info(f"{response.body.decode()}")
            return result

        def _is_webpage(self, response: Response):
            return isinstance(response, TextResponse)

        def spider_closed(self, spider):
            # This will be called when the spider is closed
            self.logger.info("Spider closed: %s", spider.name)
            directory = f"data/{self.name}"
            folder_count = sum(
                os.path.isdir(os.path.join(directory, entry))
                for entry in os.listdir(directory)
            )

            self.logger.info(f"Scraped {folder_count} products")
            # shutil.rmtree(f'data/{self.allowed_domains[0]}')

    return GenericSpider
