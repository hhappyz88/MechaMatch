from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request, Response, TextResponse
from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import Generator, cast
from scrapy import signals
import json
import os

# import shutil
from toy_catalogue.settings import silence_scrapy_logs


def create_spider(input_rules: tuple[Rule]) -> type[CrawlSpider]:
    class GenericSpider(CrawlSpider):
        name = "site_spider"
        rules = input_rules

        def __init__(self, start_urls: list[str], *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_urls = start_urls
            self.allowed_domains = [urlparse(url).netloc for url in start_urls]
            silence_scrapy_logs()

        @classmethod
        def from_crawler(cls, crawler, *args, **kwargs):
            # Pull param from crawler settings if needed
            spider = super().from_crawler(crawler, *args, **kwargs)
            crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
            return spider

        def parse_start_url(self, response: Response, **kwargs):
            if self.is_bad_response(response):
                yield self.retry_request(response)
                return []
            return []

        def parse_page(self, response: Response):
            if self.is_bad_response(response):
                yield self.retry_request(response)
                return
            # Log all links extracted on this page
            try:
                self.logger.info(f"Currently on page: {response.url}")
            except Exception as e:
                self.logger.error(f"Error in parse_page: {e}")
                return

        def parse_item(self, response: Response) -> Generator[Request, None, None]:
            if self.is_bad_response(response) and not self._is_webpage(response):
                yield self.retry_request(response)
                return
            response = cast(TextResponse, response)
            self.logger.debug(f"Found product: {response.url}")
            try:
                # Create folder for domain
                domain = self.allowed_domains[0]
                page_id = urlparse(response.url).path.replace("/", "_").lstrip("_")
                path = f"data/{domain}/{page_id}"
                os.makedirs(path, exist_ok=True)
                os.makedirs(f"{path}/images", exist_ok=True)
                # Save raw HTML
                with open(os.path.join(path, "page.html"), "wb") as f:
                    f.write(response.body)

                # Extract and download images
                for i, img_url in enumerate(response.css("img::attr(src)").getall()):
                    img_url = response.urljoin(img_url)
                    yield Request(
                        img_url,
                        callback=self.save_image,
                        meta={"path": path, "index": i},
                    )

                # Save metadata (title, etc.)
                metadata = {
                    "url": response.url,
                    "title": response.css("title::text").get(default="").strip(),
                    "time": datetime.now(timezone.utc).isoformat(),
                    "encoding": response.encoding,
                }
                with open(os.path.join(path, "metadata.json"), "w") as f:
                    f.write(json.dumps(metadata, indent=2))
            except Exception as e:
                self.logger.error(f"Error in parse_item: {e}")
                return

        def save_image(self, response: Response):
            try:
                path = response.meta["path"]
                index = response.meta["index"]
                filename = os.path.join(path, f"images/image_{index}.jpg")
                with open(filename, "wb") as f:
                    f.write(response.body)
            except Exception as e:
                self.logger.error(f"Error in save_image: {e}")
                return

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
            # ProxyManager().mark_failure(request.meta.get("proxy"))
            # new_meta["proxy"] = ProxyManager().get_url()  # Optional: get a new proxy
            return request.replace(dont_filter=True, meta=new_meta)

        def is_bad_response(self, response):
            # Check for Cloudflare captcha, login redirect, etc.
            return (
                response.status != 200
                or b"remote_addr" in response.body.lower()
                and b"http_user-agent" in response.body.lower()
            )

        def _is_webpage(self, response: Response):
            return isinstance(response, TextResponse)

        def spider_closed(self, spider):
            # This will be called when the spider is closed
            self.logger.info("Spider closed: %s", spider.name)
            directory = f"data/{self.allowed_domains[0]}"
            folder_count = sum(
                os.path.isdir(os.path.join(directory, entry))
                for entry in os.listdir(directory)
            )

            self.logger.info(f"Scraped {folder_count} products")
            # shutil.rmtree(f'data/{self.allowed_domains[0]}')

    return GenericSpider
