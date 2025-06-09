from __future__ import annotations
from pathlib import Path
from moduscrape.processing.items._base import BaseItem
from typing import Any, TYPE_CHECKING
from scrapy.http import Response

if TYPE_CHECKING:
    from moduscrape.runtime.registry import ServiceRegistry


class SaveModifier:
    @staticmethod
    def get_save_destination(
        item: BaseItem, registry: ServiceRegistry, meta_key: str
    ) -> Path:
        folder_path: Path = registry.session_dir / registry.input_config.site
        return folder_path

    @staticmethod
    def extract_meta_from_response(response: Response) -> Any | None:
        return None
