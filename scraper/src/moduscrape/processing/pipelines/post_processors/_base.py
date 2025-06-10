from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional, TYPE_CHECKING
from moduscrape.processing.items._base import BaseItem
from scrapy.http import Request, Response
from moduscrape.runtime.session_logger import SessionLoggerMixin

if TYPE_CHECKING:
    from moduscrape.runtime.registry import ServiceRegistry


class BasePostProcessor(ABC, SessionLoggerMixin):
    """
    Abstract base class for processors that:
    1. Define how to insert metadata into Scrapy Request.meta
    2. Define how to process that metadata later during scraping or pipelines

    Override _process to for processing behaviour
    """

    meta_key: str

    def __init__(self, method: str, registry: ServiceRegistry):
        self.registry = registry

    def insert_meta(
        self, request: Request, response: Optional[Response] = None, **kwargs: Any
    ) -> Request:
        """
        Preprocessor that inserts additional meta information into a Request
        Args:
            request (Request): Original Scrapy Request
            response (Optional[Response], optional): _description_. Defaults to None.

        Returns:
            Request: Unmodified Request or Request with updated meta information
        """
        meta_value = None
        if response:
            meta_value = self._extract_meta_from_response(response)
        else:
            meta_value = kwargs.get("meta_value")
        # If no meta to add, just return the original request unchanged
        if meta_value is None:
            return request

        new_meta = dict(request.meta or {})
        new_meta[self.meta_key] = meta_value
        return request.replace(meta=new_meta)

    def _extract_meta_from_response(self, response: Response) -> Optional[Any]:
        return None

    def process(self, item: BaseItem) -> BaseItem:
        try:
            processed_item = self._process(item)
            self.log_success(
                source=f"processing.pipelines.post_processors.base.{self.meta_key}",
                msg=f"Successfully processed {item.state} for {item.url}",
            )
            return processed_item
        except Exception as e:
            self.log_error(
                source=f"processing.pipelines.post_processors.base.{self.meta_key}",
                msg=f"Failed to process {item} for {item.url}",
                err=e,
            )
            return item

    @abstractmethod
    def _process(self, item: BaseItem) -> BaseItem:
        ...

    @abstractmethod
    def already_been_processed(self, item: BaseItem) -> bool:
        ...
