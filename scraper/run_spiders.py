from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from toy_catalogue.spiders.spider_factory import (
    create_spider,
)  # Import your spider
from toy_catalogue.spiders.rule_factory import (
    create_rules,
)  # Import your rule factory
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))  # /your_project_root/scraper
sys.path.insert(0, project_root)

# Set Scrapy settings module
os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "toy_catalogue.settings")
get_project_settings().get("REQUEST_FINGERPRINTER_IMPLEMENTATION")
# DynamicSpider = create_spider(
#     catalogue_format='/shop/',
#     product_format='/product/'
# )  # Create the spider dynamically
# process.crawl(DynamicSpider, start_url='https://sugotoys.com.au')
# DynamicSpider = create_spider(
#     catalogue_format=r'/products/[0-9]+\.html',
#     product_format=r'/[A-Za-z0-9\-]+_p[0-9]+\.html'
# )  # Create the spider dynamically

# process.crawl(
#     Spider,
#     start_urls=["https://gundamit.com/products/"],
# )
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Incorrect Usage, try: python scraper/run_spiders.py website")
        sys.exit(1)
    process = CrawlerProcess(get_project_settings())  # Load settings.py

    rule_config = create_rules(sys.argv[1])
    print(rule_config)
    Spider = create_spider(rule_config)  # Create the spider dynamically
    process.crawl(Spider)
    process.start()  # Blocks until all spiders finish
