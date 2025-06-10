from __future__ import annotations
from scrapy.http import Request, Response
from typing import Callable, TYPE_CHECKING
from moduscrape.utils.url import canonicalise_url
import logging
from moduscrape.processing.items import from_response
from moduscrape.runtime.session_logger import SessionLoggerMixin

if TYPE_CHECKING:
    from moduscrape.processing.items._base import BaseItem
    from moduscrape.runtime.registry import ServiceRegistry


class BaseCrawlStrategy(SessionLoggerMixin):
    """
    Base strategy class at the core of state traversal

    Can be extended by overriding _filter_links function_
    """

    seen: set[str]

    def __init__(self, registry: ServiceRegistry) -> None:
        """
        Initialise a new BaseStrategy

        Args:
            registry (ServiceRegistry):
              - registry object containing preprocessors and state traversal graph
        """
        self.registry = registry
        self.seen = set()

    def make_callback(self) -> Callable[[Response], list[Request | BaseItem]]:
        """
        Returns subsequent function to be callbacked once previous request is complete
        Returns:
            Callable[[Response], list[Request | BaseItem]]: callback
        """
        return self._get_new_requests

    def _get_new_requests(self, response: Response) -> list[Request | BaseItem]:
        logger = logging.getLogger(__name__)
        current_state: str | None = response.meta.get("callback")
        if current_state is None:
            logger.warning(f"No callback state in meta for {response.url}")
            return []
        logger.debug(f"{response.url} crawled originating from {current_state}")

        try:
            item = from_response(response, current_state)
            self.log_success(
                source="response_to_item_parse",
                msg=f"Item created successfully {type(item)}",
            )
        except Exception as e:
            self.log_error(
                source="response_to_item_parse",
                msg=f"Item creation failed for: {response.url}",
                err=e,
            )
            item = None

        all_outputs: list[Request | BaseItem] = [item] if item else []
        node_edges = self.registry.graph.get(current_state, {})
        if node_edges:
            for next_node, extractors in node_edges.items():
                for extractor in extractors:
                    raw_urls = extractor.extract(response)
                    filtered_urls = self._filter_links(
                        current_state, next_node, raw_urls
                    )
                    for url in filtered_urls:
                        all_outputs.append(
                            self._wrap_request(
                                Request(
                                    url,
                                    callback=self.make_callback(),
                                    meta={"callback": next_node},
                                ),
                                response,
                            )
                        )
        self.log_event(
            event_type="links_extracted",
            source="strategy",
            details={
                "count": len(all_outputs)
                - int(not isinstance(all_outputs[0], Request)),
                "url": response.url,
            },
        )
        return all_outputs

    def _filter_links(self, from_node: str, to_node: str, urls: list[str]) -> list[str]:
        return self._filter_duplicates(urls)

    def _filter_duplicates(self, urls: list[str]) -> list[str]:
        result: list[str] = []
        for url in urls:
            if canonicalise_url(url) not in self.seen:
                self.seen.add(canonicalise_url(url))
                result.append(url)
        return result

    def _wrap_request(self, request: Request, response: Response) -> Request:
        for processor in self.registry.get_processors():
            request = processor.insert_meta(request, response)
        return request
