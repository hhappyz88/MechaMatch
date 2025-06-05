from .base import BaseCrawlStrategy
from .strategies.fresh import FreshCrawlStrategy
from ..graph import TraversalGraph
from toy_catalogue.config.schema.external.schema import StrategyConfig
from toy_catalogue.session.session_manager import SessionContext

STRATEGY_REGISTRY: dict[str, type[BaseCrawlStrategy]] = {"fresh": FreshCrawlStrategy}


def register_strategy(name: str, strategy: type[BaseCrawlStrategy]) -> None:
    STRATEGY_REGISTRY[name] = strategy


def get_strategy(name: str) -> type[BaseCrawlStrategy]:
    return STRATEGY_REGISTRY[name]


def build_strategy(
    strategy_config: StrategyConfig,
    traversal_graph: TraversalGraph,
    session: SessionContext,
) -> BaseCrawlStrategy:
    strategy_cls = STRATEGY_REGISTRY.get(strategy_config.name)
    if not strategy_cls:
        raise ValueError(f"Unknown strategy: {strategy_config.name}")
    return strategy_cls(traversal_graph, session=session)
