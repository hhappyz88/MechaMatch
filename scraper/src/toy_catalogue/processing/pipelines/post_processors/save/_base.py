from abc import abstractmethod
from typing import Any

from scrapy.http import Response
from .._base import BasePostProcessor
from toy_catalogue.utils.session_manager import SessionContext
from toy_catalogue.processing.items import BaseItem
from .path.registry import SAVE_TYPES
from .path.base import SaveModifier
from pathlib import Path
import json
from toy_catalogue.utils.paths import make_safe_folder_name


class SavePostProcessor(BasePostProcessor):
    meta_key: str = "save"
    path_saver: type[SaveModifier]

    def __init__(self, method: str):
        self.path_saver = SAVE_TYPES.get(method) or SAVE_TYPES["default"]

    def process(self, item: BaseItem, context: SessionContext) -> BaseItem:
        self.save(item, context)
        return item

    def get_save_path(self, item: BaseItem, context: SessionContext) -> Path:
        base = self.path_saver.get_save_destination(item, context, self.meta_key)
        subfolder = self.get_content_subfolder(item)
        return base / subfolder / make_safe_folder_name(item.id)

    def save(self, item: BaseItem, context: SessionContext) -> None:
        folder_path = self.get_save_path(item, context)
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

    def extract_meta_from_response(self, response: Response) -> Any | None:
        return self.path_saver.extract_meta_from_response(response)

    def already_been_processed(self, item: BaseItem, context: SessionContext) -> bool:
        folder_path = self.get_save_path(item, context)
        return (folder_path / "metadata.json").exists()

    @abstractmethod
    def get_content_filename(self, item: BaseItem) -> str:
        ...

    def get_content_subfolder(self, item: BaseItem) -> str:
        # Optional: override if you want different folders for types
        return ""  # default to no subfolder
