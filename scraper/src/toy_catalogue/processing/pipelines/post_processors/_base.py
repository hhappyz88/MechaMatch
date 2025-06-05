from abc import ABC, abstractmethod
from typing import Any, Optional
from toy_catalogue.session.session_manager import SessionContext
from toy_catalogue.processing.items import BaseItem
from scrapy.http import Request, Response


class BasePostProcessor(ABC):
    """
    Abstract base class for processors that:
    1. Define how to insert metadata into Scrapy Request.meta
    2. Define how to process that metadata later during scraping or pipelines
    """

    meta_key: str

    def __init__(self, method: str):
        pass

    def insert_meta(
        self, request: Request, response: Optional[Response] = None, **kwargs: Any
    ) -> Request:
        meta_value = None
        if response:
            meta_value = self.extract_meta_from_response(response)
        else:
            meta_value = kwargs.get("meta_value")
        # If no meta to add, just return the original request unchanged
        if meta_value is None:
            return request

        new_meta = dict(request.meta or {})
        new_meta[self.meta_key] = meta_value
        return request.replace(meta=new_meta)

    def extract_meta_from_response(self, response: Response) -> Optional[Any]:
        return None

    def process(self, item: BaseItem, context: SessionContext) -> BaseItem:
        try:
            processed_item = self._process(item, context)
            context.record_success(
                source=f"processing.pipelines.post_processors.base.{self.meta_key}",
                msg=f"Successfully processed {item.state} for {item.url}",
            )
            return processed_item
        except Exception as e:
            context.record_error(
                source=f"processing.pipelines.post_processors.base.{self.meta_key}",
                msg=f"Failed to process {item.state} for {item.url}",
                error=e,
            )
            return item

    @abstractmethod
    def _process(self, item: BaseItem, context: SessionContext) -> BaseItem:
        ...

    @abstractmethod
    def already_been_processed(self, item: BaseItem, context: SessionContext) -> bool:
        ...
