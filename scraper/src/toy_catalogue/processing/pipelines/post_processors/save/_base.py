from abc import abstractmethod
from typing import Any

from scrapy.http import Response
from .._base import BasePostProcessor
from toy_catalogue.utils.session_manager import SessionContext
from toy_catalogue.processing.items import BaseItem
from .path.registry import SAVE_TYPES
from .path.base import SaveModifier


class SavePostProcessor(BasePostProcessor):
    meta_key: str = "save"
    path_saver: type[SaveModifier]

    def __init__(self, method: str):
        self.path_saver = SAVE_TYPES.get(method) or SAVE_TYPES["default"]

    @abstractmethod
    def save(self, item: BaseItem, context: SessionContext) -> None:
        pass

    def process(self, item: BaseItem, context: SessionContext) -> BaseItem:
        self.save(item, context)
        return item

    def extract_meta_from_response(self, response: Response) -> Any | None:
        return self.path_saver.extract_meta_from_response(response)
