from scrapy.http import Response, TextResponse
from toy_catalogue.extractors._base import BaseExtractor
from scrapy import linkextractors
from toy_catalogue.extractors._base import ExtractorParam
from typing import Callable, Optional


class LEParams(ExtractorParam):
    # Refer to https://docs.scrapy.org/en/latest/topics/link-extractors.html#scrapy.linkextractors.lxmlhtml.LxmlLinkExtractor
    allow: Optional[str | list[str]] = None
    deny: Optional[str | list[str]] = None
    allow_domains: Optional[str | list[str]] = None
    deny_domains: Optional[str | list[str]] = None
    deny_extensions: Optional[str | list[str]] = None
    restrict_xpaths: Optional[str | list[str]] = None
    restrict_css: Optional[str | list[str]] = None
    restrict_text: Optional[str | list[str]] = None
    tags: Optional[str | list[str]] = None
    attrs: Optional[list[str]] = None
    canonicalize: Optional[bool] = None
    unique: Optional[bool] = None
    process_value: Optional[Callable] = None
    strip: Optional[bool] = None


class LinkExtractor(BaseExtractor):
    def __init__(self, params: LEParams):
        kwargs = {k: v for k, v in params.model_dump(exclude_none=True).items()}
        self.le = linkextractors.LinkExtractor(**kwargs)

    def extract(self, response: Response) -> list[str]:
        if not isinstance(response, TextResponse):
            raise TypeError(f"Response {response} is not Type TextResponse")
        return [link.url for link in self.le.extract_links(response)]
