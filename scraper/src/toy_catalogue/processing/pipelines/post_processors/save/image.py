from ._base import SavePostProcessor
from toy_catalogue.utils.session_manager import SessionContext
from toy_catalogue.processing.items import BaseItem
from urllib.parse import urlparse
from pathlib import Path
import json
from toy_catalogue.utils.paths import make_safe_folder_name


class ImageSaveProcessor(SavePostProcessor):
    def save(self, item: BaseItem, context: SessionContext) -> None:
        image_bytes = item.content
        image_url = item.url
        metadata = item.metadata
        # Use image URL path to generate a safe filename
        parsed = urlparse(image_url)
        image_filename = Path(parsed.path).name
        if not image_filename:
            image_filename = "image"

        # Determine a deterministic folder to store the image
        folder_path = self.path_saver.get_save_destination(item, context, self.meta_key)
        folder_path.mkdir(parents=True, exist_ok=True)

        # Save image file
        try:
            image_path = folder_path / "images" / make_safe_folder_name(image_filename)
            image_path.mkdir(parents=True, exist_ok=True)
            (image_path / image_filename).write_bytes(image_bytes)

            # Save metadata (optional, e.g. alt text, source page)
            meta_path = image_path / "metadata.json"
            meta_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            print(e)
