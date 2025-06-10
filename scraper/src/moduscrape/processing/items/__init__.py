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
    """
    Parses content from scrapy response into pydantic model for later processing
    Args:
        response (Response): scrapy Response
        state (str): Traversal state of site where the response was obtained from

    Returns:
        BaseItem:
          - Pydantic model that by default stores id, state, url, content and metadata
    """
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
