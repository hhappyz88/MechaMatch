from pydantic import BaseModel, Field, ValidationInfo, ConfigDict, field_validator
from typing import Any
from moduscrape.engine.extractors import get_extractor, get_extractor_keys
from moduscrape.engine.extractors._base import ExtractorParam


class ExtractorConfig(BaseModel):
    class_: str = Field(..., alias="class")
    params: ExtractorParam

    @field_validator("params", mode="before")
    @classmethod
    def cast_params(cls, value: Any, info: ValidationInfo) -> ExtractorParam:
        class_name = info.data["class_"]
        if isinstance(value, dict):
            if class_name not in get_extractor_keys():
                raise ValueError(f"Unknown extractor class: {class_name}")
            param_cls, _ = get_extractor(class_name)
            return param_cls.model_validate(value)
        return value

    model_config = ConfigDict(arbitrary_types_allowed=True)
