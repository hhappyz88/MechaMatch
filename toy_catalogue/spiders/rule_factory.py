from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import json


def create_rules(websites: list[str]):
    for website in websites:
        try:
            with open(f"data/{website}/rules.json", "r") as f:
                rules = json.load(f)
            for rule in rules:
                rule["link_extractor"] = LinkExtractor(**rule["link_extractor"])
            return [Rule(**rule) for rule in rules]
        except FileNotFoundError:
            print(
                f"Rules file for {website} not found."
                + " Please create a rules.json file in the data/{website} directory."
            )
            return []
        except json.JSONDecodeError:
            print(
                f"Error decoding JSON for {website}. Please check the rules.json file."
            )
            return []
        except Exception as e:
            print(f"An error occurred while loading rules for {website}: {e}")
            return []
