from abc import ABC, abstractmethod
from typing import Any
from toy_catalogue.utils.session_manager import SessionContext


class BasePostProcessor(ABC):
    @abstractmethod
    def process(self, item: Any, context: SessionContext) -> Any:
        pass
