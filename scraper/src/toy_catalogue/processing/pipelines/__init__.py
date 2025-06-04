# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from __future__ import annotations
from .post_processors import ItemProcessorPairing
from scrapy.crawler import Crawler
from typing import Any, TYPE_CHECKING, cast
from toy_catalogue.spiders.generic_spider import GenericSpider

if TYPE_CHECKING:
    from toy_catalogue.config.schema.external.schema import ProcessorSchema
    from toy_catalogue.processing.items import BaseItem
from .post_processors import PROCESSOR_REGISTRY


class PostProcessingPipeline:
    def __init__(self, registry: dict[str, list[ItemProcessorPairing]]):
        self.registry = registry

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "PostProcessingPipeline":
        spider = cast(GenericSpider, crawler.spider)
        registry = cls.build_mapping(spider.session_context.meta.config.processors)
        return cls(registry)

    @staticmethod
    def build_mapping(config: ProcessorSchema) -> dict[str, list[ItemProcessorPairing]]:
        mapping: dict[str, list[ItemProcessorPairing]] = {}
        for state, nodes in config.root.items():
            mapping[state] = [PROCESSOR_REGISTRY[name] for name in nodes]
        return mapping

    def process_item(self, item: BaseItem, spider: GenericSpider) -> Any:
        for type_registry in self.registry[item.state]:
            processor = type_registry.get(type(item))
            if processor is None:
                return item
            item = processor.process(item, spider.session_context)
        return item
