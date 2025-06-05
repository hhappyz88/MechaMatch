from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toy_catalogue.config.schema.external.schema import ExtractorSchema

from ._base import BaseExtractor, ExtractorParam
from .css import CssParams, CssGetExtractor, CssGetAllExtractor
from .link_extractor import LinkExtractor, LEParams


EXTRACTOR_REGISTRY: dict[str, tuple[type[ExtractorParam], type[BaseExtractor]]] = {
    "css_get": (CssParams, CssGetExtractor),
    "css_getall": (CssParams, CssGetAllExtractor),
    "link_extractor": (LEParams, LinkExtractor),
}


def register_extractor(
    name: str, cls_params: type[ExtractorParam], cls: type[BaseExtractor]
) -> None:
    EXTRACTOR_REGISTRY[name] = (cls_params, cls)


def get_extractor(name: str) -> tuple[type[ExtractorParam], type[BaseExtractor]]:
    return EXTRACTOR_REGISTRY[name]


def build_extractor(config: ExtractorSchema) -> BaseExtractor:
    registered = EXTRACTOR_REGISTRY.get(config.class_)
    if not registered:
        raise ValueError(f"Unknown extractor: {config.class_}")
    return registered[1](config.params)
