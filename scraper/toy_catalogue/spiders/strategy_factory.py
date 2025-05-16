from scrapy.linkextractors import LinkExtractor
from scrapy.http import TextResponse
from typing import Any, Callable
from scrapy_playwright.page import PageMethod


def create_product_strategy(
    strategy: str, **kwargs
) -> Callable[[TextResponse], list[str]]:
    if strategy == "link_extractor":

        def result(response: TextResponse) -> list[str]:
            return [lin.url for lin in LinkExtractor(**kwargs).extract_links(response)]

        return result
    else:
        raise KeyError(f"No strategy {strategy} found")


def create_pagination_strategy(
    strategy: str, **kwargs
) -> Callable[[TextResponse], str | None]:
    if strategy == "next_button":
        if "selector" not in kwargs.keys():
            raise KeyError("Missing selector for next_button pagination strategy")

        def result(response: TextResponse) -> str | None:
            return response.css(f"{kwargs['selector']}::attr(href)").get()

        return result
    else:
        raise KeyError(f"No strategy {strategy} found")


def create_playwright_strategy(raw_config: dict[str, Any]) -> dict[str, Any]:
    if len(raw_config) == 0:
        return {}
    playwright_config = raw_config.get("playwright", {})
    page_methods = []
    for m in raw_config.get("page_methods", []):
        page_methods.append(PageMethod(m["method"], *m["args"]))
    context = playwright_config.get("context", {})
    return {
        "playwright": True,
        "playwright_page_methods": page_methods,
        "play_wright_context": context,
    }
