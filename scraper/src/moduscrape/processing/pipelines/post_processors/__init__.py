from typing import Mapping, TypeAlias
from .save import SAVE_POST_PROCESSOR_REGISTRY
from ._base import BasePostProcessor
from moduscrape.processing.items._base import BaseItem

ItemProcessorPairing: TypeAlias = Mapping[type[BaseItem], type[BasePostProcessor]]
PROCESSOR_REGISTRY: Mapping[str, ItemProcessorPairing] = {
    "save": SAVE_POST_PROCESSOR_REGISTRY,
}
