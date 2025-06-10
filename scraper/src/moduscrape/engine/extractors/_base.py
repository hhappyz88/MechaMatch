from abc import ABC, abstractmethod
from scrapy.http import Response
from typing import Any
from pydantic import BaseModel


class ExtractorParam(BaseModel):
    """
    Abstract data structure for configuration of Extractor
    """


class BaseExtractor(ABC):
    """
    Abstract class for Extractors that parse scrapy Responses
    Args:
        ABC (_type_): _description_
    """

    @abstractmethod
    def __init__(self, params: ExtractorParam):
        """
        Initialise the Extractor
        Args:
            params (ExtractorParam): Verified ExtractorParam for the class
        """

    @abstractmethod
    def extract(self, response: Response) -> list[Any]:
        """
        Extract links from scrapy response based on configurations
        Args:
            response (Response): Scrapy Response object

        Returns:
            list[Any]: list of objects
        """
