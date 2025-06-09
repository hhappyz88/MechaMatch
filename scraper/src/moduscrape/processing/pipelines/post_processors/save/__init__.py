from ._base import SavePostProcessor
from .html import HTMLSaveProcessor
from .image import ImageSaveProcessor
from moduscrape.processing.items._base import BaseItem
from moduscrape.processing.items.html import HtmlItem
from moduscrape.processing.items.image import ImageItem
from typing import Mapping

SAVE_POST_PROCESSOR_REGISTRY: Mapping[type[BaseItem], type[SavePostProcessor]] = {
    HtmlItem: HTMLSaveProcessor,
    ImageItem: ImageSaveProcessor,
}
