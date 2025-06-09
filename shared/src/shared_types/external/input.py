from pydantic import BaseModel
from .processors import ProcessorConfig
from .traversal_graph import TraversalGraphConfig


class InputConfig(BaseModel):
    site: str
    start_urls: dict[str, str]
    traversal: TraversalGraphConfig
    processors: ProcessorConfig
