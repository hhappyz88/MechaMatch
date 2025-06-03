from ._base import BaseCrawlStrategy
from .fresh import FreshCrawlStrategy
from ..graph import TraversalGraph
from toy_catalogue.config.schema.internal.schema import StrategyConfig

__all__ = ["BaseCrawlStrategy"]

STRATEGY_REGISTRY: dict[str, type[BaseCrawlStrategy]] = {"fresh": FreshCrawlStrategy}


def build_strategy(
    strategy_config: StrategyConfig, traversal_graph: TraversalGraph
) -> BaseCrawlStrategy:
    strategy_cls = STRATEGY_REGISTRY.get(strategy_config.name)
    if not strategy_cls:
        raise ValueError(f"Unknown strategy: {strategy_config.name}")
    return strategy_cls(traversal_graph)
