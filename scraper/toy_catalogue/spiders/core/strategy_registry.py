from toy_catalogue.spiders.crawl_strategies._base import BaseCrawlStrategy
from toy_catalogue.spiders.crawl_strategies.fresh import FreshCrawlStrategy


STRATEGY_REGISTRY: dict[str, type[BaseCrawlStrategy]] = {"fresh": FreshCrawlStrategy}
