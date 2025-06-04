from __future__ import annotations
import json
from ._base import SavePostProcessor
from typing import TYPE_CHECKING

from toy_catalogue.processing.items import BaseItem
from toy_catalogue.utils.paths import make_safe_folder_name

if TYPE_CHECKING:
    from toy_catalogue.utils.session_manager import SessionContext


class HTMLSaveProcessor(SavePostProcessor):
    def save(self, item: BaseItem, context: SessionContext) -> None:
        content = item.content
        metadata = item.metadata

        folder_path = self.path_saver.get_save_destination(
            item, context, self.meta_key
        ) / make_safe_folder_name(item.id)
        folder_path.mkdir(parents=True, exist_ok=True)

        # Save raw HTML
        html_path = folder_path / "page.html"
        html_path.write_bytes(content)

        # Construct and save metadata

        meta_path = folder_path / "metadata.json"
        meta_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
        )
