from datetime import datetime, timezone
from pydantic import Field
from scrapy.http import Response
from ._base import BaseItem
from typing import Any


class ImageItem(BaseItem):
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    format: str = Field(..., description="Image format, e.g., 'jpeg', 'png'")
    alt_text: str = Field(default="", description="Alternative text if available")
    downloaded_at: str = Field(..., description="ISO timestamp of download time")
    source_page_url: str = Field(
        ..., description="URL of the page that linked to this image"
    )

    @classmethod
    def _extra_from_response(cls, response: Response) -> dict[str, Any]:
        img_format = (
            (response.headers.get("Content-Type") or b"image/unknown")
            .decode(errors="replace")
            .split("/")[-1]
        )
        return {
            "width": 0,
            "height": 0,
            "format": img_format,
            "alt_text": response.meta.get("alt", ""),
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
            "source_page_url": response.meta.get("source_page", ""),
        }
