from pydantic import BaseModel, RootModel, Field, field_validator, ConfigDict
from typing import Any
from toy_catalogue.extractors._base import ExtractorParam
from toy_catalogue.core.extractor_registry import EXTRACTOR_REGISTRY


class ExtractorConfig(BaseModel):
    class_: str = Field(..., alias="class")
    params: ExtractorParam

    @field_validator("params", mode="before")
    @classmethod
    def cast_params(cls, value: Any, info: Any) -> ExtractorParam:
        class_name = info.data["class_"]
        if isinstance(value, dict):
            if class_name not in EXTRACTOR_REGISTRY:
                raise ValueError(f"Unknown extractor class: {class_name}")
            param_cls, _ = EXTRACTOR_REGISTRY[class_name]
            return param_cls.model_validate(value)
        return value  # already validated

    model_config = ConfigDict(arbitrary_types_allowed=True)


class NodeConfig(BaseModel):
    extractors: list[ExtractorConfig]
    callbacks: list[str] = []
    recurse: bool = False


class GraphConfig(RootModel[dict[str, list[NodeConfig]]]):
    def get_node(self, node: str) -> list[NodeConfig]:
        return self.root.get(node, [])


class SiteConfig(BaseModel):
    site: str
    start_urls: dict[str, str]
    traversal: GraphConfig


class StrategyConfig(BaseModel):
    name: str
    params: dict
