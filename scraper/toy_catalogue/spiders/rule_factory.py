from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import json
import logging

logger = logging.getLogger(__name__)


def create_rules(websites: list[str]) -> list[Rule]:
    for website in websites:
        try:
            with open(f"config/scrapy_rules/{website}.json", "r") as f:
                rules = json.load(f)
            parsed_rules = []
            for rule in rules:
                logger.info(f"Input rules: {rule}")
                link_extractor_config = rule.pop("link_extractor")
                le = LinkExtractor(**link_extractor_config)
                callback = rule.get("callback", None)
                follow = rule.get("follow", False)
                process_links = rule.get("process_links", None)
                process_request = rule.get("process_request", None)
                errback = rule.get("errback", None)

                # Construct Rule with all arguments
                parsed_rules.append(
                    Rule(
                        link_extractor=le,
                        callback=callback,
                        follow=follow,
                        process_links=process_links,
                        process_request=process_request,
                        errback=errback,
                    )
                )
            return parsed_rules
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
    return []
