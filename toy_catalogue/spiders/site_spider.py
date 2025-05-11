from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from urllib.parse import urlparse, parse_qs, urlunparse
from datetime import datetime, timezone
import json
import os
import time


def normalize_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Remove unwanted query parameters like 'sort', 'page', etc.
    query_params.pop("sort", None)  # Example of removing 'sort'
    query_params.pop("page", None)  # Example of removing 'page'

    # Rebuild the URL without those parameters
    normalized_query = "&".join(f"{k}={v[0]}" for k, v in query_params.items())
    normalized_url = urlunparse(parsed_url._replace(query=normalized_query))

    return normalized_url


class SiteSpider(CrawlSpider):
    name = "site_spider"

    # handle_httpstatus_list = [429]
    def __init__(self, start_url: str, depth: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.allowed_domains = [urlparse(start_url).netloc]
        if depth:
            self.depth = int(depth)

    rules = (
        Rule(
            LinkExtractor(deny=[r"\?.*"]),  # allow all on domain
            callback="parse_page",
            follow=True,
        ),
    )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # Pull param from crawler settings if needed
        my_param = crawler.settings.get("depth", None)
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.my_param = my_param
        return spider

    def parse_page(self, response):
        self.logger.info(f"Crawled URL: {response.url}")
        if response.status == 429:
            retry_after = response.headers.get("Retry-After")
            self.logger.info(f"429 error encountered. Retry-After: {retry_after}")
            print(retry_after)
            if retry_after:
                wait_time = int(retry_after)
                self.logger.info(f"Retrying after {wait_time} seconds")
                time.sleep(wait_time)
            yield Request(response.url, callback=self.parse_page)
            return

        # Create folder for domain
        domain = urlparse(response.url).netloc
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
                img_url, callback=self.save_image, meta={"path": path, "index": i}
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

    def save_image(self, response):
        path = response.meta["path"]
        index = response.meta["index"]
        filename = os.path.join(path, f"images/image_{index}.jpg")
        with open(filename, "wb") as f:
            f.write(response.body)
