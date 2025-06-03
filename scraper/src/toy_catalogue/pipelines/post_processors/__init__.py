from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...
from ._base import BasePostProcessor
from .html_save import HTMLSaveProcessor

PROCESSOR_REGISTRY: dict[str, type[BasePostProcessor]] = {
    "HTMLSave": HTMLSaveProcessor,
}
