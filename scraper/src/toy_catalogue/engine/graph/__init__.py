from ..extractors import build_extractor
from ..extractors._base import BaseExtractor
from toy_catalogue.config.schema.internal.schema import GraphSchema
from typing import TypeAlias

TraversalGraph: TypeAlias = dict[str, dict[str, list[BaseExtractor]]]


def build_traversal_graph(graph_config: GraphSchema) -> TraversalGraph:
    graph: TraversalGraph = {}
    for name, details in graph_config.root.items():
        graph[name] = {}
        for detail in details:
            for callback in detail.callbacks:
                for extractor in detail.extractors:
                    new_ext = [build_extractor(extractor)]
                    graph[name][callback] = graph[name].get(callback, []) + new_ext
    return graph
