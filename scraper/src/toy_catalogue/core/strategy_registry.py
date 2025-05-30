from toy_catalogue.crawl_strategies._base import BaseCrawlStrategy
from toy_catalogue.crawl_strategies.fresh import FreshCrawlStrategy


STRATEGY_REGISTRY: dict[str, type[BaseCrawlStrategy]] = {"fresh": FreshCrawlStrategy}
