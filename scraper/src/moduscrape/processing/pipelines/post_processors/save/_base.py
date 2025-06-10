from __future__ import annotations
from abc import abstractmethod
from typing import Any, TYPE_CHECKING

from scrapy.http import Response
from .._base import BasePostProcessor
from moduscrape.processing.items._base import BaseItem
from .path.registry import SAVE_TYPES
from .path.base import SaveModifier
from pathlib import Path
import json
from moduscrape.utils.paths import make_safe_folder_name

if TYPE_CHECKING:
    from moduscrape.runtime.registry import ServiceRegistry


class SavePostProcessor(BasePostProcessor):
    """
    Saves the entire item to harddrive
    """

    meta_key: str = "save"
    path_saver: type[SaveModifier]

    def __init__(self, method: str, registry: ServiceRegistry):
        super().__init__(method, registry)
        self.path_saver = SAVE_TYPES.get(method) or SAVE_TYPES["default"]

    def _process(self, item: BaseItem) -> BaseItem:
        self.save(item)
        return item

    def get_save_path(self, item: BaseItem) -> Path:
        base = self.path_saver.get_save_destination(item, self.registry, self.meta_key)
        subfolder = self.get_content_subfolder(item)
        return base / subfolder / make_safe_folder_name(item.id)

    def save(self, item: BaseItem) -> None:
        folder_path = self.get_save_path(item)
        folder_path.mkdir(parents=True, exist_ok=True)

        # Save content
        content_path = folder_path / self.get_content_filename(item)
        content_path.write_bytes(item.content)

        # Save metadata
        meta_path = folder_path / "metadata.json"
        meta_path.write_text(
            json.dumps(
                {"filename": self.get_content_filename(item), **item.metadata},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def _extract_meta_from_response(self, response: Response) -> Any | None:
        return self.path_saver.extract_meta_from_response(response)

    def already_been_processed(self, item: BaseItem) -> bool:
        folder_path = self.get_save_path(item)
        return (folder_path / "metadata.json").exists()

    @abstractmethod
    def get_content_filename(self, item: BaseItem) -> str:
        ...

    def get_content_subfolder(self, item: BaseItem) -> str:
        # Optional: override if you want different folders for types
        return ""  # default to no subfolder
