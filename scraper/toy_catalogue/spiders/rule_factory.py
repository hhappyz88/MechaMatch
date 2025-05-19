from scrapy.http import TextResponse
import json
import logging
import os
from itertools import product
from typing import TypedDict, Callable, Any, Optional, Union
import sys
from toy_catalogue.spiders.strategy_factory import (
    create_pagination_strategy,
    create_product_strategy,
    create_playwright_strategy,
)

logger = logging.getLogger(__name__)

CompatibleKey = Union[str, int, float, None]


class SpiderConfig(TypedDict):
    site: str
    start_urls: list[str]
    playwright: dict[CompatibleKey, Any]
    pagination_strategy: Callable[[TextResponse], Optional[str]]
    pagination_meta: dict[str, Any]
    product_strategy: Callable[[TextResponse], list[str]]
    product_meta: dict[str, Any]
    image_format: str


def playwright_settings() -> dict[CompatibleKey, Any]:
    return {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False,  # Show the browser (can help bypass bot detection)
            # Optional: add slow_mo to slow down actions for realism
            # "slow_mo": 100,
        },
        "SCRAPE_PLAYWRIGHT_ENABLED": True,
        "PLAYWRIGHT_MAX_CONTEXTS": 8,
    }


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
        result: SpiderConfig = {
            "site": name,
            "start_urls": config["start_urls"],
            "playwright": {},
            "pagination_strategy": create_pagination_strategy(
                strategy=pagination_strategy, **config["pagination_strategy"]
            ),
            "pagination_meta": {},
            "product_strategy": create_product_strategy(
                strategy=product_strategy, **config["product_strategy"]
            ),
            "product_meta": {},
            "image_format": ", ".join(image_formats),
        }
        if config.get("playwright"):
            result["playwright"] = playwright_settings()
            result["pagination_meta"].update(
                create_playwright_strategy(
                    config["playwright"].get("playwright_pagination", {})
                )
            )
            result["product_meta"].update(
                create_playwright_strategy(
                    config["playwright"].get("playwright_product", {})
                )
            )
        return result

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
