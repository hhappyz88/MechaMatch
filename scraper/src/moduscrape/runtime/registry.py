from __future__ import annotations
from typing import Any, TYPE_CHECKING
from moduscrape.engine.crawl import build_strategy
from shared_types.external.input import InputConfig
from moduscrape.engine.graph import TraversalGraph
from moduscrape.session.session_logger import SessionLogger, SessionLoggerAdapter
from moduscrape.config.parameters import SESSION_BASE_DIR
from pathlib import Path
import json
from datetime import datetime
import logging

from moduscrape.processing.pipelines import ProcessorPipeline, ProcessorMapping

if TYPE_CHECKING:
    from moduscrape.engine.crawl.base import BaseCrawlStrategy
    from scrapy.crawler import Crawler
    from moduscrape.processing.pipelines.post_processors._base import BasePostProcessor


class ServiceRegistry:
    session_id: str
    session_dir: Path

    input_config: InputConfig
    crawler: Crawler
    logger: SessionLogger
    strategy: BaseCrawlStrategy
    graph: TraversalGraph
    runtime_state: dict[str, Any]
    post_process_map: ProcessorMapping

    def __init__(self, mode: str, config: InputConfig) -> None:
        self.input_config = config
        self.logger = SessionLogger(self)
        self.strategy = build_strategy(mode=mode, registry=self)
        self.graph = TraversalGraph(config.traversal)

        index_file = SESSION_BASE_DIR / "index.jsonl"

        timestamp = datetime.now()
        now_str = timestamp.strftime(
            "%Y-%m-%dT%H-%M-%S"
        )  # FIXME: make utility function for datetime to string
        tags = None  # TODO: allow tags to passed as an input
        tag_str = "_".join(tags) if tags else "no-tag"
        session_id = f"{now_str}_{config.site}_{tag_str}"

        self.session_dir = SESSION_BASE_DIR / session_id
        self.session_dir.mkdir(parents=True, exist_ok=False)
        with open(self.session_dir / "meta.json", "w") as f:
            json.dump(config.model_dump(), f, indent=2)

        with open(index_file, "a", encoding="utf-8") as index:
            index.write(config.model_dump_json() + "\n")

        adapter = SessionLoggerAdapter(self.logger)
        logging.getLogger().addHandler(adapter)

        self.post_process_map = ProcessorPipeline.build_mapping(self)

    def register_crawler(self, crawler: Crawler) -> None:
        self.crawler = crawler

    def get_processors(self) -> list[BasePostProcessor]:
        results: list[BasePostProcessor] = []
        for sub_map in self.post_process_map.values():
            for processors in sub_map.values():
                results.extend(processors)
        return results
