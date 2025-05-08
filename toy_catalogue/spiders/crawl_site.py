import scrapy
import os
from urllib.parse import urlparse


class CrawlSiteSpider(scrapy.Spider):
    name = "crawl_site"

    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not start_url:
            raise ValueError("start_url must be provided")
        self.start_urls = [start_url]
        self.allowed_domain = urlparse(start_url).netloc

    def parse(self, response):
        # Save raw HTML
        parsed_url = urlparse(response.url)
        filename = parsed_url.path.strip("/").replace("/", "_") or "index"
        os.makedirs(f"data/{self.allowed_domain}", exist_ok=True)
        filepath = f"data/{self.allowed_domain}/{filename}"

        with open(filepath, "wb") as f:
            f.write(response.body)

        # Follow internal links
        for href in response.css("a::attr(href)").getall():
            url = response.urljoin(href)
            if urlparse(url).netloc == self.allowed_domain:
                yield scrapy.Request(url, callback=self.parse)
