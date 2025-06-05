from ._base import SavePostProcessor

from toy_catalogue.processing.items import BaseItem


class HTMLSaveProcessor(SavePostProcessor):
    def get_content_filename(self, item: BaseItem) -> str:
        return "page.html"
