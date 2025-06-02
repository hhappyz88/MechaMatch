from scrapy.spiders import Spider
from scrapy.http import Request, Response, TextResponse
from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import AsyncGenerator
from scrapy import signals

from toy_catalogue.utils.url import canonicalise_url
from toy_catalogue.core.strategy_factory import build_strategy
from toy_catalogue.schema.config_schema import StrategyConfig
from toy_catalogue.core.handler_factory import build_handler_graph
from toy_catalogue.utils.session_manager import SessionContext


class GenericSpider(Spider):
    name = "generic"

    def __init__(self, context: SessionContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_urls: set[str] = set()
        self.checkpoint_data: dict[str, str] = {}
        self.start_urls = list(context.meta.config.start_urls.values())
        self.parse_methods = list(context.meta.config.start_urls.keys())
        self.allowed_domains = [urlparse(url).netloc for url in self.start_urls]
        self.start_time = datetime.now(timezone.utc)
        mode_config = StrategyConfig.model_validate(
            {"name": context.meta.mode, "params": {}}
        )
        traversal_graph = build_handler_graph(context.meta.config.traversal)
        self.strategy = build_strategy(mode_config, traversal_graph)
        # silence_scrapy_logs()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
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
        # self.state["checkpoint"] = self.checkpoint_data
        self.logger.info("Spider closed: %s", spider.name)

        duration = datetime.now(timezone.utc) - self.start_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.logger.info(f"Run took {hours:02}h {minutes:02}mins {seconds:02}s")

        # update_job_list(
        #     self, {"name": self.name, "start_time": self.start_time.isoformat()}
        # )
