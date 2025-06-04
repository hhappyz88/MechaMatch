from __future__ import annotations
from abc import ABC
from scrapy.http import Request, Response
from typing import Callable, TYPE_CHECKING
from toy_catalogue.utils.url import canonicalise_url
import logging
from ..graph import TraversalGraph
from toy_catalogue.processing.items import from_response

if TYPE_CHECKING:
    from toy_catalogue.processing.items._base import BaseItem
    from toy_catalogue.processing.pipelines.post_processors import BasePostProcessor


class BaseCrawlStrategy(ABC):
    graph: TraversalGraph
    seen: set[str]

    def __init__(self, traversal_graph: TraversalGraph) -> None:
        self.graph = traversal_graph
        self.seen = set()

    def add_meta_processors(self, processors: list[BasePostProcessor]):
        self.processors = processors

    def make_callback(self) -> Callable[[Response], list[Request | BaseItem]]:
        def _callback(response: Response) -> list[Request | BaseItem]:
            outputs: list[Request | BaseItem] = []
            for output in self.process_node(response):
                if isinstance(output, Request):
                    for p in self.processors:
                        output = p.insert_meta(output, response)
                outputs.append(output)
            return outputs

        return _callback

    def process_node(self, response: Response) -> list[Request | BaseItem]:
        logger = logging.getLogger(__name__)
        current_state: str | None = response.meta.get("callback")
        if current_state is None:
            logger.warning(f"No callback state in meta for {response.url}")
            return []
        logger.debug(f"{response.url} crawled originating from {current_state}")

        all_outputs: list[Request | BaseItem] = [from_response(response, current_state)]
        node_edges = self.graph.get(current_state, {})
        if node_edges:
            for next_node, extractors in node_edges.items():
                for extractor in extractors:
                    raw_urls = extractor.extract(response)
                    filtered_urls = self.filter_links(
                        current_state, next_node, raw_urls
                    )
                    for url in filtered_urls:
                        all_outputs.append(
                            Request(
                                url,
                                callback=self.make_callback(),
                                meta={"callback": next_node},
                            )
                        )

        return all_outputs

    def filter_links(self, from_node: str, to_node: str, urls: list[str]) -> list[str]:
        return self._filter_duplicates(urls)

    def _filter_duplicates(self, urls: list[str]) -> list[str]:
        result: list[str] = []
        for url in urls:
            if canonicalise_url(url) not in self.seen:
                self.seen.add(canonicalise_url(url))
                result.append(url)
        return result
