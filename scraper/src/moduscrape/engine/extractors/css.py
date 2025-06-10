from scrapy.http import Response, TextResponse
from ._base import BaseExtractor, ExtractorParam
from itertools import product


class CssParams(ExtractorParam):
    selectors: list[str]
    attrs: list[str]


class CssGetExtractor(BaseExtractor):
    __css_selector: list[str]
    __attrs: list[str]

    def __init__(self, params: CssParams) -> None:
        self.__css_selector = params.selectors
        self.__attrs = params.attrs

    def extract(self, response: Response) -> list[str]:
        if not isinstance(response, TextResponse):
            raise TypeError(f"Response {response} is not Type TextResponse")
        results: list[str] = []
        for selector, attr in product(self.__css_selector, self.__attrs):
            val = response.css(f"{selector}::attr({attr})").get()
            if val:
                results.append(response.urljoin(val))
        return results


class CssGetAllExtractor(BaseExtractor):
    __css_selector: list[str]
    __attrs: list[str]

    def __init__(self, params: CssParams) -> None:
        self.__css_selector = params.selectors
        self.__attrs = params.attrs

    def extract(self, response: Response) -> list[str]:
        """
        Extracts css content from TextResponse
        Args:
            response (Response): scrapy TextResponse

        Raises:
            TypeError: response is not TextResponse

        Returns:
            list[str]: extracted content
        """
        if not isinstance(response, TextResponse):
            raise TypeError(f"Response {response} is not Type TextResponse")

        results: list[str] = []
        for selector, attr in product(self.__css_selector, self.__attrs):
            css_query = f"{selector}::attr({attr})"
            extracted = response.css(
                css_query
            ).getall()  # getall to get all matches per query
            results.extend(response.urljoin(link) for link in extracted)
        return results
