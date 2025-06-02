from toy_catalogue.core.extractor_factory import build_extractor
from toy_catalogue.schema.config_schema import GraphConfig
from toy_catalogue.extractors._base import BaseExtractor
from typing import TypeAlias

HandlerGraph: TypeAlias = dict[str, dict[str, list[BaseExtractor]]]


def build_handler_graph(graph_config: GraphConfig) -> HandlerGraph:
    graph: HandlerGraph = {}
    for name, details in graph_config.root.items():
        graph[name] = {}
        for detail in details:
            for callback in detail.callbacks:
                for extractor in detail.extractors:
                    new_ext = [build_extractor(extractor)]
                    graph[name][callback] = graph[name].get(callback, []) + new_ext
    return graph
