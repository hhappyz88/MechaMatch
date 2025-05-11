from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from urllib.parse import urlparse
from datetime import datetime, timezone
import json
import os
import time


def create_spider(input_rules: tuple[Rule]):
    class DynamicSpider(CrawlSpider):
        name = "site_spider"
        handle_httpstatus_list = [429]

        def __init__(self, start_urls: list[str], depth: str = None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_urls = start_urls
            self.allowed_domains = [urlparse(url).netloc for url in start_urls]
            if depth:
                self.depth = int(depth)

        rules = input_rules

        @classmethod
        def from_crawler(cls, crawler, *args, **kwargs):
            # Pull param from crawler settings if needed
            catalogue_format = crawler.settings.get("depth", None)
            spider = super().from_crawler(crawler, *args, **kwargs)
            spider.catalogue_format = catalogue_format
            return spider

        def parse_page(self, response):
            self.logger.info(f"Parsing: {response.url}")
            # Log all links extracted on this page
            links = LinkExtractor(
                allow=["/[A-Za-z0-9\\-]+_p[0-9]+\\.html"], deny=["\\?.*"]
            ).extract_links(response)
            for link in links:
                self.logger.info(f"Found link: {link.url}")
            try:
                self.logger.info(f"Currently on page: {response.url}")
                if response.status == 429:
                    retry_after = response.headers.get("Retry-After")
                    self.logger.info(
                        f"429 error encountered. Retry-After: {retry_after}"
                    )
                    print(retry_after)
                    if retry_after:
                        wait_time = int(retry_after)
                        self.logger.info(f"Retrying after {wait_time} seconds")
                        time.sleep(wait_time)
                    yield Request(response.url, callback=self.parse_page)
            except Exception as e:
                self.logger.error(f"Error in parse_page: {e}")
                return

        def parse_item(self, response):
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

        def save_image(self, response):
            try:
                path = response.meta["path"]
                index = response.meta["index"]
                filename = os.path.join(path, f"images/image_{index}.jpg")
                with open(filename, "wb") as f:
                    f.write(response.body)
            except Exception as e:
                self.logger.error(f"Error in save_image: {e}")
                return

    return DynamicSpider
