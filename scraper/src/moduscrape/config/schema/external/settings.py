from typing import Optional
from pydantic import BaseModel, Field, RootModel


class RegistryConfig(RootModel[dict[str, int]]):
    pass


class CustomConfig(BaseModel):
    images_store: Optional[str] = None
    log_level: Optional[str] = None


class ScrapySettings(BaseModel):
    concurrent_requests: Optional[int] = Field(default=16, alias="CONCURRENT_REQUESTS")
    autothrottle_enabled: Optional[bool] = Field(
        default=True, alias="AUTOTHROTTLE_ENABLED"
    )
    download_delay: Optional[float] = Field(default=0, alias="DOWNLOAD_DELAY")


class FullConfig(BaseModel):
    scrapy: Optional[ScrapySettings] = None
    pipelines: Optional[RegistryConfig] = None
    downloader_middlewares: Optional[RegistryConfig] = None
    spider_middlewares: Optional[RegistryConfig] = None
    extensions: Optional[RegistryConfig] = None
    custom: Optional[CustomConfig] = None
