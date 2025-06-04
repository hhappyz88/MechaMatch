from abc import abstractmethod
from .._base import BasePostProcessor
from toy_catalogue.utils.session_manager import SessionContext
from toy_catalogue.processing.items import BaseItem


class SavePostProcessor(BasePostProcessor):
    @abstractmethod
    def save(self, item: BaseItem, context: SessionContext) -> None:
        pass

    def process(self, item: BaseItem, context: SessionContext) -> None:
        self.save(item, context)
