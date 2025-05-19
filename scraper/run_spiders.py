import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from toy_catalogue.spiders.spider_factory import (
    create_spider,
)  # Import your spider
from toy_catalogue.spiders.rule_factory import (
    create_rules,
)  # Import your rule factory


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Incorrect Usage, try: python scraper/run_spiders.py website")
        sys.exit(1)
    process = CrawlerProcess(get_project_settings())  # Load settings.py

    rule_config = create_rules(sys.argv[1])
    print(f"Rules created {rule_config}")
    Spider = create_spider(rule_config)  # Create the spider dynamically
    print("Spider created")
    process.crawl(Spider)
    print("Crawler was added")  # Should print

    process.start()
    print("Crawler finished")  # Blocks until all spiders finish
