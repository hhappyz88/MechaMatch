from scrapy.http import Response, TextResponse
from toy_catalogue.extractors._base import BaseExtractor, ExtractorParam
from itertools import product


class CssParams(ExtractorParam):
    selectors: list[str]
    attrs: list[str]


class CssGetExtractor(BaseExtractor):
    def __init__(self, params: CssParams) -> None:
        self.css_selector = params.selectors
        self.attr = params.attrs

    def extract(self, response: Response) -> list[str]:
        if not isinstance(response, TextResponse):
            raise TypeError(f"Response {response} is not Type TextResponse")
        results = []
        for selector, attr in product(self.css_selector, self.attr):
            val = response.css(f"{selector}::attr({attr})").get()
            if val:
                results.append(response.urljoin(val))
        return results


class CssGetAllExtractor(BaseExtractor):
    def __init__(self, params: CssParams) -> None:
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
