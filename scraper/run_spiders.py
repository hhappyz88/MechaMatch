import sys
from scrapy.crawler import CrawlerProcess
from toy_catalogue.utils.settings_manager import create_settings
from toy_catalogue.spiders.spider_factory import (
    create_spider,
)  # Import your spider
import json
import os
from scrapy.utils.project import get_project_settings


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Incorrect Usage, try: python scraper/run_spiders.py website")
        sys.exit(1)

    # rule_config = create_rules(sys.argv[1])
    settings = create_settings(sys.argv[1])
    rule_path = os.path.join(
        "toy_catalogue", "config", "scrapy_rules", f"{sys.argv[1]}.json"
    )
    with open(rule_path, "r") as f:
        config = json.load(f)
    Spider = create_spider(config)  # Create the spider dynamically
    print("Spider created")
    # process = CrawlerProcess(settings)  # Load settings.py
    process = CrawlerProcess(get_project_settings())
    process.crawl(Spider)
    print("Crawler was added")  # Should print

    process.start()
    print("Crawler finished")  # Blocks until all spiders finish
