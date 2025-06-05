from abc import ABC, abstractmethod
from scrapy.http import Response
from typing import Any
from pydantic import BaseModel


class ExtractorParam(BaseModel):
    ...


class BaseExtractor(ABC):
    @abstractmethod
    def __init__(self, params: ExtractorParam):
        ...

    @abstractmethod
    def extract(self, response: Response) -> list[Any]:
        ...
