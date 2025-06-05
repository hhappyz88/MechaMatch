from toy_catalogue.session.session_manager import SessionContext
from pathlib import Path
from toy_catalogue.processing.items import BaseItem
from typing import Any
from scrapy.http import Response


class SaveModifier:
    @staticmethod
    def get_save_destination(
        item: BaseItem, context: SessionContext, meta_key: str
    ) -> Path:
        folder_path: Path = context.session_dir / context.meta.site
        return folder_path

    @staticmethod
    def extract_meta_from_response(response: Response) -> Any | None:
        return None
