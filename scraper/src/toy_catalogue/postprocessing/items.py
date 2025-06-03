# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy import Item, Field


class ProductItem(Item):
    url = Field()
    data = Field()


class ImageItem(Item):
    url = Field()
    image_url = Field()
