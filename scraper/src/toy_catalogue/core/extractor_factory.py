from toy_catalogue.extractors._base import BaseExtractor
from toy_catalogue.schema.config_schema import ExtractorConfig
from toy_catalogue.core.extractor_registry import EXTRACTOR_REGISTRY


def build_extractor(config: ExtractorConfig) -> BaseExtractor:
    if not isinstance(config, ExtractorConfig):
        raise TypeError(f"Expected ExtractorConfig, got {type(config)}")

    registered = EXTRACTOR_REGISTRY.get(config.class_)
    if not registered:
        raise ValueError(f"Unknown extractor: {config.class_}")
    return registered[1](config.params)
