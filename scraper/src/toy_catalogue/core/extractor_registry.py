from toy_catalogue.extractors._base import BaseExtractor, ExtractorParam
from toy_catalogue.extractors.css import (
    CssGetExtractor,
    CssGetAllExtractor,
    CssParams,
)
from toy_catalogue.extractors.link_extractor import LinkExtractor, LEParams

EXTRACTOR_REGISTRY: dict[str, tuple[type[ExtractorParam], type[BaseExtractor]]] = {
    "css_get": (CssParams, CssGetExtractor),
    "css_getall": (CssParams, CssGetAllExtractor),
    "link_extractor": (LEParams, LinkExtractor),
}
