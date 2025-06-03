from __future__ import annotations
from pydantic import BaseModel, RootModel, Field, field_validator, ConfigDict
from typing import Any

from toy_catalogue.engine.extractors import EXTRACTOR_REGISTRY, ExtractorParam


class ExtractorSchema(BaseModel):
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


class NodeSchema(BaseModel):
    extractors: list[ExtractorSchema]
    callbacks: list[str] = []


class GraphSchema(RootModel[dict[str, list[NodeSchema]]]):
    def get_node(self, node: str) -> list[NodeSchema]:
        return self.root.get(node, [])


class SiteConfig(BaseModel):
    site: str
    start_urls: dict[str, str]
    traversal: GraphSchema


class StrategyConfig(BaseModel):
    name: str
    # params: dict
