from typing import Mapping, TypeAlias
from .save import SAVE_POST_PROCESSOR_REGISTRY
from ._base import BasePostProcessor
from toy_catalogue.processing.items import BaseItem

ItemProcessorPairing: TypeAlias = Mapping[type[BaseItem], type[BasePostProcessor]]
PROCESSOR_REGISTRY: Mapping[str, ItemProcessorPairing] = {
    "save": SAVE_POST_PROCESSOR_REGISTRY,
}
