from scrapy.http import TextResponse
import json
import logging
import os
from itertools import product
from typing import TypedDict, Callable, Any, Optional
import sys
from toy_catalogue.spiders.strategy_factory import (
    create_pagination_strategy,
    create_product_strategy,
    create_playwright_strategy,
)

logger = logging.getLogger(__name__)


class SpiderConfig(TypedDict):
    site: str
    start_urls: list[str]
    pagination_strategy: Callable[[TextResponse], Optional[str]]
    pagination_meta: dict[str, Any]
    product_strategy: Callable[[TextResponse], list[str]]
    product_meta: dict[str, Any]
    image_format: str


def create_rules(name: str) -> SpiderConfig:
    try:
        rule_path = os.path.join("config", "scrapy_rules", f"{name}.json")
        with open(rule_path, "r") as f:
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
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON for {name}. Please check the rules.json file.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while loading rules for {name}: {e}")
        sys.exit(1)
