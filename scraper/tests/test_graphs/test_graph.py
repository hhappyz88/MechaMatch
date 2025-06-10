from moduscrape.engine.graph import TraversalGraph
from moduscrape.engine.extractors._base import BaseExtractor
from shared_types.external.traversal_graph import (
    TraversalGraphConfig,
)  # Adjust if you have this class
from itertools import chain


def test_graph_structure_matches_config(sample_graph_config: TraversalGraphConfig):
    graph = TraversalGraph(sample_graph_config)

    for state, submap in sample_graph_config.root.items():
        callbacks = chain.from_iterable(node.callbacks for node in submap)
        assert state in graph.get_all()
        for cb in callbacks:
            assert cb in graph[state]


def test_extractors_are_instantiated(sample_graph_config: TraversalGraphConfig):
    graph = TraversalGraph(sample_graph_config)

    for callback_map in graph.get_all().values():
        for extractors in callback_map.values():
            for extractor in extractors:
                # update to match your path
                assert isinstance(extractor, BaseExtractor)


def test_extractor_has_expected_interface(sample_graph_config: TraversalGraphConfig):
    graph = TraversalGraph(sample_graph_config)
    sample_extractor = next(iter(next(iter(graph.get_all().values())).values()))[0]

    assert callable(sample_extractor.extract)


def test_graph_get(sample_graph_config: TraversalGraphConfig):
    graph = TraversalGraph(sample_graph_config)
    assert graph.get("doesnt exist", {}) == {}
    assert graph.get(list(sample_graph_config.root.keys())[0], {}) != {}
