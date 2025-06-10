from ..extractors import build_extractor
from ..extractors._base import BaseExtractor
from shared_types.external.traversal_graph import TraversalGraphConfig
from pydantic import BaseModel, PrivateAttr


class TraversalGraph(BaseModel):
    """
    Mapping of states to callbacks and associated link extractors
    Content can be fetched via dictionary methods
    """

    _graph: dict[str, dict[str, list[BaseExtractor]]] = PrivateAttr()

    def __init__(self, graph_config: TraversalGraphConfig) -> None:
        self._graph = {}
        for name, details in graph_config.root.items():
            self._graph[name] = {}
            for detail in details:
                for callback in detail.callbacks:
                    for extractor in detail.extractors:
                        new_ext = [build_extractor(extractor)]
                        self._graph[name][callback] = (
                            self._graph[name].get(callback, []) + new_ext
                        )

    def __getitem__(self, key: str) -> dict[str, list[BaseExtractor]]:
        return self._graph[key]

    def get(
        self, key: str, default: dict[str, list[BaseExtractor]] = {}
    ) -> dict[str, list[BaseExtractor]]:
        return self._graph.get(key, default)

    def get_all(self) -> dict[str, dict[str, list[BaseExtractor]]]:
        return self._graph
