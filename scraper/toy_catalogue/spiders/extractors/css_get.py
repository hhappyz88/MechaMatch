from scrapy.http import Response, TextResponse
from toy_catalogue.spiders.extractors._base import BaseExtractor, ExtractorParam
from itertools import product


class CssGetParams(ExtractorParam):
    selectors: list[str]
    attrs: list[str]


class CssGetExtractor(BaseExtractor):
    def __init__(self, params: CssGetParams) -> None:
        self.css_selector = params.selectors
        self.attr = params.attrs

    def extract(self, response: Response) -> list[str]:
        if not isinstance(response, TextResponse):
            raise TypeError(f"Response {response} is not Type TextResponse")
        results = []
        for selector, attr in product(self.css_selector, self.attr):
            val = response.css(f"{selector}::attr({attr})").get()
            if val:
                results.append(val)
        return results
