from ._base import SavePostProcessor
from .html import HTMLSaveProcessor
from .image import ImageSaveProcessor
from toy_catalogue.processing.items import BaseItem, HtmlItem, ImageItem
from typing import Mapping

SAVE_POST_PROCESSOR_REGISTRY: Mapping[type[BaseItem], type[SavePostProcessor]] = {
    HtmlItem: HTMLSaveProcessor,
    ImageItem: ImageSaveProcessor,
}
