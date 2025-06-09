from ._base import SavePostProcessor

from moduscrape.processing.items._base import BaseItem


class HTMLSaveProcessor(SavePostProcessor):
    def get_content_filename(self, item: BaseItem) -> str:
        return "page.html"
