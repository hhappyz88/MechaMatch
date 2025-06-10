from scrapy.http import Response, TextResponse
from ._base import BaseExtractor, ExtractorParam
from scrapy.linkextractors import LinkExtractor as ScrapyLE
from typing import Callable, Optional, Any


class LEParams(ExtractorParam):
    # Refer to https://docs.scrapy.org/en/latest/topics/link-extractors.html#scrapy.linkextractors.lxmlhtml.LxmlLinkExtractor
    allow: Optional[str | list[str]] = None
    deny: Optional[str | list[str]] = None
    allow_domains: Optional[str | list[str]] = None
    deny_domains: Optional[str | list[str]] = None
    deny_extensions: Optional[str | list[str]] = []
    restrict_xpaths: Optional[str | list[str]] = None
    restrict_css: Optional[str | list[str]] = None
    restrict_text: Optional[str | list[str]] = None
    tags: Optional[str | list[str]] = None
    attrs: Optional[list[str]] = ["href", "data-href"]
    canonicalize: Optional[bool] = True
    unique: Optional[bool] = True
    process_value: Optional[Callable[[Any], Any]] = None


class LinkExtractor(BaseExtractor):
    __le: ScrapyLE

    def __init__(self, params: LEParams):
        kwargs = {k: v for k, v in params.model_dump(exclude_none=True).items()}
        self.__le = ScrapyLE(**kwargs)

    def extract(self, response: Response) -> list[str]:
        if not isinstance(response, TextResponse):
            raise TypeError(f"Response {response} is not Type TextResponse")
        return [link.url for link in self.__le.extract_links(response)]
