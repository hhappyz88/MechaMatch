from ._base import SavePostProcessor
from moduscrape.processing.items._base import BaseItem

import mimetypes
import hashlib


class ImageSaveProcessor(SavePostProcessor):
    def get_content_filename(self, item: BaseItem) -> str:
        # Try to get file extension from Content-Type
        mime_type = item.metadata.get("headers", {}).get("Content-Type", [""])[0]
        ext = mimetypes.guess_extension(mime_type) or ".bin"

        # Use a hash of the URL to ensure uniqueness
        url_hash = hashlib.md5(item.url.encode("utf-8")).hexdigest()[:8]

        return f"image_{url_hash}{ext}"
