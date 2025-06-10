# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from __future__ import annotations
from scrapy.crawler import Crawler
from typing import Any, TYPE_CHECKING, TypeAlias
from .post_processors import PROCESSOR_REGISTRY
from scrapy.spiders import Spider
from moduscrape.runtime.session_logger import SessionLoggerMixin
from scrapy import signals
from moduscrape.processing.pipelines.post_processors._base import BasePostProcessor
from moduscrape.processing.items._base import BaseItem

if TYPE_CHECKING:
    from moduscrape.spiders.core_spider import CoreSpider
    from moduscrape.runtime.registry import ServiceRegistry

ProcessorMapping: TypeAlias = dict[str, dict[type[BaseItem], list[BasePostProcessor]]]


class ProcessorPipeline(SessionLoggerMixin):
    """
    Processor Pipeline that directs Items to their correct processor
    """

    _initialised: bool = False

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> ProcessorPipeline:
        instance = cls()
        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        return instance

    def spider_opened(self, spider: Spider) -> None:
        """
        Delayed setup of pipeline as crawler does not have spider instantiated yet
        """
        if not self._initialised:
            registry = getattr(spider, "registry", None)
            if registry is None:
                raise TypeError("Spider does not expose a `registry` attribute.")
            self.registry = registry
            self._initialised = True

    @staticmethod
    def build_mapping(registry: ServiceRegistry) -> ProcessorMapping:
        """
        Creates mapping of state to item type and processor
        """
        mapping: ProcessorMapping = {}
        for state, nodes in registry.input_config.processors.root.items():
            proc_mapping = [
                (name.get("method", "default"), PROCESSOR_REGISTRY[name["class"]])
                for name in nodes
            ]
            for param, sub_prob_mapping in proc_mapping:
                mapping[state] = {}
                for item, processor in sub_prob_mapping.items():
                    mapping[state][item] = mapping[state].get(item, []) + [
                        processor(param, registry)
                    ]
        return mapping

    def process_item(self, item: BaseItem, spider: CoreSpider) -> Any:
        registries = self.registry.post_process_map.get(item.state)
        if registries is None:
            return item
        processors = registries.get(type(item))
        if processors is None:
            return item
        for processor in processors:
            item = processor.process(item)
        return item
