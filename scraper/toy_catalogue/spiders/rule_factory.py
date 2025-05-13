from scrapy.linkextractors import LinkExtractor
import json
import logging
from typing import TypedDict

logger = logging.getLogger(__name__)


class ConfigFile(TypedDict):
    start_url: str
    collection_le: dict[str, str]
    page_le: dict[str, str]


class SpiderConfig(TypedDict):
    name: str
    start_url: str
    collection_le: LinkExtractor
    page_le: LinkExtractor


def create_rules(name: str) -> SpiderConfig | None:
    try:
        with open(f"scraper/config/scrapy_rules/{name}.json", "r") as f:
            config = json.load(f)
        return {
            "name": name,
            "start_url": config["start_url"],
            "collection_le": LinkExtractor(**config["collection_le"]),
            "page_le": LinkExtractor(**config["page_le"]),
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
