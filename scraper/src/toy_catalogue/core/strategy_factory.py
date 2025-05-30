from toy_catalogue.crawl_strategies._base import BaseCrawlStrategy
from toy_catalogue.schema.config_schema import StrategyConfig, GraphConfig
from toy_catalogue.core.strategy_registry import STRATEGY_REGISTRY


def build_strategy(
    strategy_config: StrategyConfig, traversal_config: GraphConfig
) -> BaseCrawlStrategy:
    if not isinstance(strategy_config, StrategyConfig):
        raise TypeError(f"Expected StrategyConfig, got {type(strategy_config)}")
    if not isinstance(traversal_config, GraphConfig):
        raise TypeError(f"Expected GraphConfig, got {type(traversal_config)}")
    strategy_cls = STRATEGY_REGISTRY.get(strategy_config.name)
    if not strategy_cls:
        raise ValueError(f"Unknown strategy: {strategy_config.name}")
    return strategy_cls(traversal_config)
