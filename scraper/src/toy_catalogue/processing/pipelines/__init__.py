# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from __future__ import annotations
from scrapy.crawler import Crawler
from typing import Any, TYPE_CHECKING, cast, TypeAlias
from toy_catalogue.spiders.generic_spider import GenericSpider

from .post_processors import PROCESSOR_REGISTRY

if TYPE_CHECKING:
    from toy_catalogue.config.schema.external.schema import ProcessorSchema
    from toy_catalogue.processing.items import BaseItem
    from toy_catalogue.processing.pipelines.post_processors import BasePostProcessor

    ProcessorMapping: TypeAlias = dict[
        str, dict[type[BaseItem], list[BasePostProcessor]]
    ]


class PostProcessingPipeline:
    def __init__(self, registry: ProcessorMapping):
        self.registry = registry

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "PostProcessingPipeline":
        spider = cast(GenericSpider, crawler.spider)
        registry, processors = cls.build_mapping(
            spider.session_context.meta.config.processors
        )
        spider.add_meta_processors(processors)
        return cls(registry)

    @staticmethod
    def build_mapping(
        config: ProcessorSchema,
    ) -> tuple[ProcessorMapping, list[BasePostProcessor]]:
        mapping: ProcessorMapping = {}
        meta_wrappers: list[BasePostProcessor] = list()
        for state, nodes in config.root.items():
            registries = [
                (name.get("method", "default"), PROCESSOR_REGISTRY[name["class"]])
                for name in nodes
            ]
            for param, registry in registries:
                mapping[state] = {}
                for item, processor in registry.items():
                    mapping[state][item] = mapping[state].get(item, []) + [
                        processor(param)
                    ]
                    meta_wrappers += mapping[state][item]
        return mapping, meta_wrappers

    def process_item(self, item: BaseItem, spider: GenericSpider) -> Any:
        registries = self.registry.get(item.state)
        if registries is None:
            return item
        processors = registries.get(type(item))
        if processors is None:
            return item
        for processor in processors:
            item = processor.process(item, spider.session_context)
        return item
