from ..extractors import build_extractor
from ..extractors._base import BaseExtractor
from shared_types.external.traversal_graph import TraversalGraphConfig


class TraversalGraph:
    graph: dict[str, dict[str, list[BaseExtractor]]]

    def __init__(self, graph_config: TraversalGraphConfig) -> None:
        self.graph = {}
        for name, details in graph_config.root.items():
            self.graph[name] = {}
            for detail in details:
                for callback in detail.callbacks:
                    for extractor in detail.extractors:
                        new_ext = [build_extractor(extractor)]
                        self.graph[name][callback] = (
                            self.graph[name].get(callback, []) + new_ext
                        )

    def __getitem__(self, key: str) -> dict[str, list[BaseExtractor]]:
        return self.graph[key]

    def get(
        self, key: str, default: dict[str, list[BaseExtractor]] = {}
    ) -> dict[str, list[BaseExtractor]]:
        return self.graph.get(key, default)
