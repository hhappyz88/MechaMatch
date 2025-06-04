from __future__ import annotations
import json
from pathlib import Path
from ._base import SavePostProcessor
from typing import TYPE_CHECKING, cast

from toy_catalogue.processing.items import BaseItem, HtmlItem

if TYPE_CHECKING:
    from toy_catalogue.utils.session_manager import SessionContext


class HTMLSaveProcessor(SavePostProcessor):
    def save(self, item: BaseItem, context: SessionContext) -> None:
        parsed_item = cast(HtmlItem, item)
        content = parsed_item.content
        metadata = parsed_item.metadata
        page_id = parsed_item.id

        folder_path: Path = context.session_dir / context.meta.site / page_id
        folder_path.mkdir(parents=True, exist_ok=True)

        # Save raw HTML
        html_path = folder_path / "page.html"
        html_path.write_bytes(content)

        # Construct and save metadata

        meta_path = folder_path / "metadata.json"
        meta_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
        )
