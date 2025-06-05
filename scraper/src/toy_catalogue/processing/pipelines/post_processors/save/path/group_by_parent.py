from typing import Any, cast
from scrapy.http import Response
from .base import SaveModifier
from toy_catalogue.session.session_manager import SessionContext
from pathlib import Path
from toy_catalogue.processing.items import BaseItem
from pydantic import BaseModel
from toy_catalogue.utils.url import generate_id
from toy_catalogue.utils.paths import make_safe_folder_name


class GBPModel(BaseModel):
    parent: str


class GroupByParent(SaveModifier):
    @staticmethod
    def get_save_destination(
        item: BaseItem, context: SessionContext, meta_key: str
    ) -> Path:
        metadata: dict[str, Any] = item.metadata  # untyped raw dict
        site: str = context.meta.site

        # Default folder path
        folder_path: Path = context.session_dir / site

        # Extract the parent ID if present in the dynamic meta
        response_meta = cast(dict[str, Any], metadata.get("response_meta"))
        dynamic_meta = cast(dict[str, Any], response_meta.get(meta_key))
        parent = dynamic_meta.get("parent")
        if isinstance(parent, str):
            folder_path = context.session_dir / site / make_safe_folder_name(parent)

        return folder_path

    @staticmethod
    def extract_meta_from_response(response: Response) -> Any | None:
        return {"parent": generate_id(response.url)}
