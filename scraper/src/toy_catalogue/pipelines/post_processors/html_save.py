from ._base import BasePostProcessor
from toy_catalogue.utils.session_manager import SessionContext
from typing import Any, cast
from ...items import StateItem
from urllib.parse import urlparse
import json
from pathlib import Path


class HTMLSaveProcessor(BasePostProcessor):
    def process(self, item: Any, context: SessionContext) -> None:
        state_item = cast(StateItem, item)
        content = state_item.content
        page_url = state_item.url
        metadata = state_item.metadata

        page_id = urlparse(page_url).path.replace("/", "_").lstrip("_")
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
