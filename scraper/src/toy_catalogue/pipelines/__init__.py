# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from __future__ import annotations
from .post_processors._base import BasePostProcessor
from scrapy.crawler import Crawler
from typing import Any, TYPE_CHECKING, cast
from toy_catalogue.spiders.generic_spider import GenericSpider

if TYPE_CHECKING:
    from toy_catalogue.config.schema.external.schema import ProcessorSchema
from .post_processors import PROCESSOR_REGISTRY


class PostProcessingPipeline:
    def __init__(self, registry: dict[str, list[BasePostProcessor]]):
        self.registry = registry

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "PostProcessingPipeline":
        spider = cast(GenericSpider, crawler.spider)
        registry = cls.build_mapping(spider.session_context.meta.config.processors)
        return cls(registry)

    @staticmethod
    def build_mapping(config: ProcessorSchema) -> dict[str, list[BasePostProcessor]]:
        mapping: dict[str, list[BasePostProcessor]] = {}
        for state, nodes in config.root.items():
            mapping[state] = [PROCESSOR_REGISTRY[name]() for name in nodes]
        return mapping

    def process_item(self, item: Any, spider: GenericSpider) -> Any:
        state = getattr(item, "state") or item.get("state")
        if not state or state not in self.registry:
            return item

        for processor in self.registry[state]:
            item = processor.process(item, spider.session_context)
        return item
