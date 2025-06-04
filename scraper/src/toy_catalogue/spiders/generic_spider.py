from scrapy.spiders import Spider
from scrapy.http import Request
from urllib.parse import urlparse
from typing import AsyncGenerator, Any
from scrapy import signals, Item
from scrapy.crawler import Crawler


from toy_catalogue.utils.url import canonicalise_url
from toy_catalogue.engine.crawl import build_strategy
from toy_catalogue.config.schema.external.schema import StrategyConfig
from toy_catalogue.engine.graph import build_traversal_graph
from toy_catalogue.utils.session_manager import SessionContext
from toy_catalogue.engine.crawl import BaseCrawlStrategy


class GenericSpider(Spider):
    name = "generic"

    session_context: SessionContext
    seen_urls: set[str] = set()
    check_point_data: dict[str, str] = {}
    strategy: BaseCrawlStrategy
    parse_methods: list[str]
    items_scraped: dict[type[Item], int]

    def __init__(self, context: SessionContext, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        # Scrapy paramters
        self.start_urls = list(context.meta.config.start_urls.values())
        self.allowed_domains = [urlparse(url).netloc for url in self.start_urls]
        self.parse_methods = list(context.meta.config.start_urls.keys())

        # Sessioning
        self.session_context = context

        # Traversal
        mode_config = StrategyConfig.model_validate(
            {"name": context.meta.mode, "params": {}}
        )
        traversal_graph = build_traversal_graph(context.meta.config.traversal)
        self.strategy = build_strategy(mode_config, traversal_graph)

        # Stats
        self.start_time = context.meta.timestamp
        # self.items_scraped = {ProductItem: 0}
        # silence_scrapy_logs()

    @classmethod
    def from_crawler(cls, crawler: Crawler, *args: Any, **kwargs: Any):
        # Pull param from crawler settings if needed
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.logger.info("from_crawler called")
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    async def start(self) -> AsyncGenerator[Request, None]:
        for url, method in zip(self.start_urls, self.parse_methods):
            yield Request(
                url,
                callback=self.strategy.make_callback(),
                meta={"callback": method},
            )

    def on_item_saved(self, item: Item) -> None:
        ...

    def _should_follow(self, urls: list[str]) -> list[str]:
        result: list[str] = []
        for link in urls:
            url = canonicalise_url(link)
            if url not in self.seen_urls:
                self.seen_urls.add(url)
                result.append(url)
        return result

    def spider_closed(self, spider: Spider) -> None:
        # This will be called when the spider is closed
        # self.state["checkpoint"] = self.checkpoint_data
        self.logger.info("Spider closed: %s", spider.name)

        # duration = datetime.now(timezone.utc) - self.start_time
        # hours, remainder = divmod(int(duration.total_seconds()), 3600)
        # minutes, seconds = divmod(remainder, 60)
        # self.logger.info(f"Run took {hours:02}h {minutes:02}mins {seconds:02}s")

        # update_job_list(
        #     self, {"name": self.name, "start_time": self.start_time.isoformat()}
        # )
