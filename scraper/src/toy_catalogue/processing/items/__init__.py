# from urllib.parse import urlparse
# from toy_catalogue.utils.session_manager import SessionContext
# from scrapy.http import Response
from .html import HtmlItem
from .image import ImageItem
from scrapy.http import Response
from ._base import BaseItem

CONTENT_TYPE_MAP: dict[str, type[BaseItem]] = {
    "text/html": HtmlItem,
    "image/jpeg": ImageItem,
    "image/png": ImageItem,
    "image/webp": ImageItem,
}


def from_response(response: Response, state: str) -> BaseItem:
    content_type: str = (
        (response.headers.get("Content-Type") or b"text/html")
        .decode(errors="replace")
        .split(";")[0]
        .strip()
        .lower()
    )

    ItemType = CONTENT_TYPE_MAP.get(content_type)
    if ItemType:
        return ItemType.from_response(response, state)
    else:
        return BaseItem.from_response(response, state)
