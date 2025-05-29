from abc import ABC
from scrapy.http import Request, Response
from typing import Callable
from toy_catalogue.spiders.core.handler_factory import build_handler_graph
from toy_catalogue.utils.url import canonicalise_url
from toy_catalogue.config.schema import GraphConfig
import logging


class BaseCrawlStrategy(ABC):
    def __init__(self, handler_configs: GraphConfig) -> None:
        self.graph = build_handler_graph(handler_configs)
        print(self.graph)
        self.seen: set[str] = set()

    def make_callback(self) -> Callable[[Response], list[Request]]:
        def _callback(response: Response) -> list[Request]:
            return self.process_node(response)

        return _callback

    def process_node(self, response: Response) -> list[Request]:
        logger = logging.getLogger(__name__)
        current_state: str | None = response.meta.get("callback")
        if current_state is None:
            logger.warning(f"No callback state in meta for {response.url}")
            return []
        logger.info(f"{response.url} crawled originating from {current_state}")

        node_edges = self.graph.get(current_state, {})
        if not node_edges:
            return []

        all_requests: list[Request] = []
        for next_node, extractors in node_edges.items():
            for extractor in extractors:
                raw_urls = extractor.extract(response)
                filtered_urls = self.filter_links(current_state, next_node, raw_urls)
                for url in filtered_urls:
                    all_requests.append(
                        Request(
                            url,
                            callback=self.make_callback(),
                            meta={"callback": next_node},
                        )
                    )

        return all_requests

    def filter_links(self, from_node: str, to_node: str, urls: list[str]) -> list[str]:
        return self._filter_duplicates(urls)

    def _filter_duplicates(self, urls: list[str]) -> list[str]:
        result: list[str] = []
        for url in urls:
            if canonicalise_url(url) not in self.seen:
                self.seen.add(canonicalise_url(url))
                result.append(url)
        return result
