from __future__ import annotations
from scrapy.spiders import Spider
from scrapy.http import Request
from urllib.parse import urlparse
from typing import AsyncGenerator, Any, TYPE_CHECKING
from scrapy import signals, Item
from scrapy.crawler import Crawler
from moduscrape.runtime.registry import ServiceRegistry

if TYPE_CHECKING:
    from shared_types.external.input import InputConfig


class CoreSpider(Spider):
    name = "core"

    check_point_data: dict[str, str]
    parse_methods: list[str]
    items_scraped: dict[type[Item], int]
    registry: ServiceRegistry

    def __init__(self, input_config: InputConfig, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Scrapy paramters
        self.start_urls = list(input_config.start_urls.values())
        self.allowed_domains = [urlparse(url).netloc for url in self.start_urls]
        self.parse_methods = list(input_config.start_urls.keys())

        # global registry for key services
        self.registry = ServiceRegistry(mode="fresh", config=input_config)

    @classmethod
    def from_crawler(cls, crawler: Crawler, *args: Any, **kwargs: Any):
        # Pull param from crawler settings if needed
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.logger.info("from_crawler called")
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        spider.registry.register_crawler(crawler)
        return spider

    async def start(self) -> AsyncGenerator[Request, None]:
        for url, method in zip(self.start_urls, self.parse_methods):
            yield Request(
                url,
                callback=self.registry.strategy.make_callback(),
                meta={"callback": method},
            )

    def spider_closed(self, spider: Spider) -> None:
        self.logger.info("Spider closed: %s", spider.name)
        self.registry.logger.flush_events_to_file()
