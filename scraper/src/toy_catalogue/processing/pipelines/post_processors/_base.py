from abc import ABC, abstractmethod
from typing import Any
from toy_catalogue.utils.session_manager import SessionContext
from toy_catalogue.processing.items import BaseItem


class BasePostProcessor(ABC):
    @abstractmethod
    def process(self, item: BaseItem, context: SessionContext) -> Any:
        pass
