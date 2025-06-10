from __future__ import annotations
from typing import TYPE_CHECKING
from .strategies.fresh import FreshCrawlStrategy
from .base import BaseCrawlStrategy

if TYPE_CHECKING:
    from moduscrape.runtime.registry import ServiceRegistry


STRATEGY_REGISTRY: dict[str, type[BaseCrawlStrategy]] = {"fresh": FreshCrawlStrategy}


def register_strategy(name: str, strategy: type[BaseCrawlStrategy]) -> None:
    STRATEGY_REGISTRY[name] = strategy


def get_strategy(name: str) -> type[BaseCrawlStrategy]:
    return STRATEGY_REGISTRY[name]


def build_strategy(mode: str, registry: ServiceRegistry) -> BaseCrawlStrategy:
    """
    Strategy factory given a mode
    Args:
        mode (str): the class of strategy to be built
        registry (ServiceRegistry): registry to be input into the Strategy

    Raises:
        ValueError: If strategy is unknown
    """
    strategy_cls = STRATEGY_REGISTRY.get(mode)
    if not strategy_cls:
        raise ValueError(f"Unknown strategy: {mode}")
    return strategy_cls(registry)
