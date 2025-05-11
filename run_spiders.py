from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from toy_catalogue.spiders.spider_factory import create_spider  # Import your spider
from toy_catalogue.spiders.rule_factory import create_rules  # Import your rule factory


process = CrawlerProcess(get_project_settings())  # Load settings.py
# DynamicSpider = create_spider(
#     catalogue_format='/shop/',
#     product_format='/product/'
# )  # Create the spider dynamically
# process.crawl(DynamicSpider, start_url='https://sugotoys.com.au')
# DynamicSpider = create_spider(
#     catalogue_format=r'/products/[0-9]+\.html',
#     product_format=r'/[A-Za-z0-9\-]+_p[0-9]+\.html'
# )  # Create the spider dynamically

rules = create_rules(["gundamit"])
Spider = create_spider(rules)  # Create the spider dynamically
process.crawl(
    Spider,
    start_urls=["https://gundamit.com/products/", "https://www.gundamit.com/products/"],
)
process.start()  # Blocks until all spiders finish
