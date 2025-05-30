from pydantic import BaseModel, HttpUrl
from typing import Literal


class FileConfig(BaseModel):
    type: Literal["file"]
    path: str


class PackageConfig(BaseModel):
    type: Literal["package"]
    resource: str


class UrlConfig(BaseModel):
    type: Literal["url"]
    url: HttpUrl


ConfigSpec = FileConfig | PackageConfig | UrlConfig
