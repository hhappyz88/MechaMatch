from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
from scrapy.http import Response
from .base import SaveModifier
from pathlib import Path
from moduscrape.processing.items._base import BaseItem
from pydantic import BaseModel
from moduscrape.utils.url import generate_id
from moduscrape.utils.paths import make_safe_folder_name

if TYPE_CHECKING:
    from moduscrape.runtime.registry import ServiceRegistry


class GBPModel(BaseModel):
    parent: str


class GroupByParent(SaveModifier):
    @staticmethod
    def get_save_destination(
        item: BaseItem, registry: ServiceRegistry, meta_key: str
    ) -> Path:
        metadata: dict[str, Any] = item.metadata  # untyped raw dict
        site: str = registry.input_config.site

        # Default folder path
        folder_path: Path = registry.session_dir / site

        # Extract the parent ID if present in the dynamic meta
        response_meta = cast(dict[str, Any], metadata.get("response_meta"))
        dynamic_meta = cast(dict[str, Any], response_meta.get(meta_key))
        parent = dynamic_meta.get("parent")
        if isinstance(parent, str):
            folder_path = registry.session_dir / site / make_safe_folder_name(parent)

        return folder_path

    @staticmethod
    def extract_meta_from_response(response: Response) -> Any | None:
        return {"parent": generate_id(response.url)}
