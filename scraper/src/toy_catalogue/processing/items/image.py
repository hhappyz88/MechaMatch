from datetime import datetime, timezone
from pydantic import Field
from scrapy.http import Response
from ._base import BaseItem
from urllib.parse import urlparse


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
    def from_response(cls, response: Response, state: str) -> "ImageItem":
        # Placeholder logic — use PIL or other image parsing tool in practice
        width = 0
        height = 0
        img_format = (
            (response.headers.get("Content-Type") or b"image/unknown")
            .decode(errors="replace")
            .split("/")[1]
        )
        alt_text = response.meta.get("alt", "")  # example: passed via meta
        source_page_url = response.meta.get("source_page", "")

        return cls(
            id=urlparse(response.url).path.replace("/", "_").lstrip("_"),
            state=state,
            url=response.url,
            content=response.body,
            width=width,
            height=height,
            format=img_format,
            alt_text=alt_text,
            downloaded_at=datetime.now(timezone.utc).isoformat(),
            source_page_url=source_page_url,
            metadata={
                "url": response.url,
                "status": response.status,
                "headers": {
                    k.decode(): [v.decode() for v in vs]
                    for k, vs in response.headers.items()
                },
            },
        )
