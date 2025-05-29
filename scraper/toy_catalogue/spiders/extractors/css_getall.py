from scrapy.http import Response, TextResponse
from toy_catalogue.spiders.extractors._base import BaseExtractor
from toy_catalogue.spiders.extractors._base import ExtractorParam
from itertools import product


class CssGetAllParams(ExtractorParam):
    selectors: list[str]
    attrs: list[str]


class CssGetAllExtractor(BaseExtractor):
    def __init__(self, params: CssGetAllParams) -> None:
        self.css_selector = params.selectors
        self.attr = params.attrs

    def extract(self, response: Response) -> list[str]:
        if not isinstance(response, TextResponse):
            raise TypeError(f"Response {response} is not Type TextResponse")

        results: list[str] = []
        for selector, attr in product(self.css_selector, self.attr):
            css_query = f"{selector}::attr({attr})"
            extracted = response.css(
                css_query
            ).getall()  # getall to get all matches per query
            results.extend(response.urljoin(link) for link in extracted)
        return results
