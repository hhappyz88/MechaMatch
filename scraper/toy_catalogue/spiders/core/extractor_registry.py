from toy_catalogue.spiders.extractors._base import BaseExtractor, ExtractorParam
from toy_catalogue.spiders.extractors.css_get import CssGetExtractor, CssGetParams
from toy_catalogue.spiders.extractors.css_getall import (
    CssGetAllExtractor,
    CssGetAllParams,
)
from toy_catalogue.spiders.extractors.link_extractor import LinkExtractor, LEParams

EXTRACTOR_REGISTRY: dict[str, tuple[type[ExtractorParam], type[BaseExtractor]]] = {
    "css_get": (CssGetParams, CssGetExtractor),
    "css_getall": (CssGetAllParams, CssGetAllExtractor),
    "link_extractor": (LEParams, LinkExtractor),
}
