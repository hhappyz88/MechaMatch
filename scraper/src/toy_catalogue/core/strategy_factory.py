from toy_catalogue.crawl_strategies._base import BaseCrawlStrategy
from toy_catalogue.schema.config_schema import StrategyConfig
from toy_catalogue.core.strategy_registry import STRATEGY_REGISTRY
from toy_catalogue.core.handler_factory import HandlerGraph


def build_strategy(
    strategy_config: StrategyConfig, traversal_graph: HandlerGraph
) -> BaseCrawlStrategy:
    strategy_cls = STRATEGY_REGISTRY.get(strategy_config.name)
    if not strategy_cls:
        raise ValueError(f"Unknown strategy: {strategy_config.name}")
    return strategy_cls(traversal_graph)
