from scrapy.http import TextResponse
import json
import logging
from itertools import product
from typing import TypedDict, Callable, Any
from toy_catalogue.spiders.strategy_factory import (
    create_pagination_strategy,
    create_product_strategy,
    create_playwright_strategy,
)

logger = logging.getLogger(__name__)


class SpiderConfig(TypedDict):
    site: str
    start_urls: list[str]
    pagination_strategy: Callable[[TextResponse], str]
    pagination_meta: dict[str, Any]
    product_strategy: Callable[[TextResponse], list[str]]
    product_meta: dict[str, Any]
    image_format: str


def create_rules(name: str) -> SpiderConfig | None:
    try:
        with open(f"scraper/config/scrapy_rules/{name}.json", "r") as f:
            config = json.load(f)

        pagination_strategy = config["pagination_strategy"].pop("type")
        product_strategy = config["product_strategy"].pop("type")
        image_formats: list[str] = []
        for selector, attrs in product(
            config["image_selectors"], config["image_attrs"]
        ):
            image_formats.append(f"{selector}::attr({attrs})")
        return {
            "site": name,
            "start_urls": config["start_urls"],
            "pagination_strategy": create_pagination_strategy(
                strategy=pagination_strategy, **config["pagination_strategy"]
            ),
            "pagination_meta": create_playwright_strategy(
                config.get("playwright", {}).get("playwright_pagination", {})
            ),
            "product_strategy": create_product_strategy(
                strategy=product_strategy, **config["product_strategy"]
            ),
            "product_meta": create_playwright_strategy(
                config.get("playwright", {}).get("playwright_product", {})
            ),
            "image_format": ", ".join(image_formats),
        }

    except FileNotFoundError:
        print(
            f"Rules file for {name} not found."
            + f" Please create a rules.json file in the data/{name} directory."
        )
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON for {name}. Please check the rules.json file.")
        return None
    except Exception as e:
        print(f"An error occurred while loading rules for {name}: {e}")
        return None
