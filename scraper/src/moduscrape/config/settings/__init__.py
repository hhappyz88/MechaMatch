import tomli
from typing import Optional, Any, cast
from importlib import resources
from pydantic import ValidationError

from scrapy.settings import Settings
from ..schema.external.settings import FullConfig  # Your Pydantic schema


def load_config_from_file(path: str) -> dict[str, Any]:
    with open(path, "rb") as f:
        return tomli.load(f)


def load_config_from_package(filename: str) -> dict[str, Any]:
    with resources.files("moduscrape.config.settings").joinpath(filename).open(
        "rb"
    ) as f:
        return tomli.load(f)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override into base."""
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = deep_merge(cast(dict[str, Any], base[k]), cast(dict[str, Any], v))
        else:
            base[k] = v
    return base


def build_settings(
    core_config: dict[str, Any], custom_config: Optional[dict[str, Any]] = None
) -> Settings:
    merged = deep_merge(core_config.copy(), custom_config or {})
    try:
        config = FullConfig.model_validate(merged)
    except ValidationError as e:
        raise RuntimeError(f"Invalid config:\n{e}")

    scrapy_settings = Settings()

    # Core Scrapy settings
    if config.scrapy:
        for k, v in config.scrapy.model_dump(exclude_none=True).items():
            scrapy_settings.set(k, v)

    registry_map = {
        "pipelines": "ITEM_PIPELINES",
        "downloader_middlewares": "DOWNLOADER_MIDDLEWARES",
        "spider_middlewares": "SPIDER_MIDDLEWARES",
        "extensions": "EXTENSIONS",
    }

    for attr, scrapy_key in registry_map.items():
        reg = getattr(config, attr)
        if reg:
            scrapy_settings.set(scrapy_key, reg.root)

    if config.custom:
        for k, v in config.custom.model_dump(exclude_none=True).items():
            scrapy_settings.set(f"CUSTOM_{k.upper()}", v)

    return scrapy_settings
