from __future__ import annotations
from typing import Any, TYPE_CHECKING
from moduscrape.engine.crawl import build_strategy
from shared_types.external.input import InputConfig
from moduscrape.engine.graph import TraversalGraph
from moduscrape.runtime.session_logger import SessionLogger, SessionLoggerAdapter
from moduscrape.config.parameters import SESSION_BASE_DIR
from pathlib import Path
from pydantic import BaseModel, PrivateAttr
import json
from datetime import datetime
import logging

from moduscrape.processing.pipelines import ProcessorPipeline, ProcessorMapping

if TYPE_CHECKING:
    from moduscrape.engine.crawl.base import BaseCrawlStrategy
    from scrapy.crawler import Crawler
    from moduscrape.processing.pipelines.post_processors._base import BasePostProcessor


class ServiceRegistry(BaseModel):
    """
    Centralised Registry to store key Singleton-like services
    """

    # Immutable startup info
    _session_id: str = PrivateAttr()
    _session_dir: Path = PrivateAttr()
    _input_config: InputConfig = PrivateAttr()

    # engine services
    _crawler: Crawler = PrivateAttr()
    _strategy: BaseCrawlStrategy = PrivateAttr()
    _graph: TraversalGraph = PrivateAttr()

    # logging information
    _runtime_state: dict[str, Any] = PrivateAttr()
    _post_process_map: ProcessorMapping = PrivateAttr()
    _logger: SessionLogger = PrivateAttr()

    def __init__(self, mode: str, config: InputConfig) -> None:
        self._input_config = config
        self._logger = SessionLogger(self)
        self._strategy = build_strategy(mode=mode, registry=self)
        self._graph = TraversalGraph(config.traversal)

        index_file = SESSION_BASE_DIR / "index.jsonl"

        timestamp = datetime.now()
        now_str = timestamp.strftime(
            "%Y-%m-%dT%H-%M-%S"
        )  # FIXME: make utility function for datetime to string
        tags = None  # TODO: allow tags to passed as an input
        tag_str = "_".join(tags) if tags else "no-tag"
        self._session_id = f"{now_str}_{config.site}_{tag_str}"

        self._session_dir = SESSION_BASE_DIR / self._session_id
        self._session_dir.mkdir(parents=True, exist_ok=False)
        with open(self._session_dir / "meta.json", "w") as f:
            json.dump(config.model_dump(), f, indent=2)

        with open(index_file, "a", encoding="utf-8") as index:
            index.write(config.model_dump_json() + "\n")

        adapter = SessionLoggerAdapter(self._logger)
        logging.getLogger().addHandler(adapter)

        self._post_process_map = ProcessorPipeline.build_mapping(self)

    def register_crawler(self, crawler: Crawler) -> None:
        self._crawler = crawler

    def get_processors(self) -> list[BasePostProcessor]:
        results: list[BasePostProcessor] = []
        for sub_map in self._post_process_map.values():
            for processors in sub_map.values():
                results.extend(processors)
        return results

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def session_dir(self) -> Path:
        return self._session_dir

    @property
    def input_config(self) -> InputConfig:
        return self._input_config

    @property
    def crawler(self) -> Crawler:
        return self._crawler

    @property
    def logger(self) -> SessionLogger:
        return self._logger

    @property
    def strategy(self) -> BaseCrawlStrategy:
        return self._strategy

    @property
    def graph(self) -> TraversalGraph:
        return self._graph

    @property
    def runtime_state(self) -> dict[str, Any]:
        return self._runtime_state

    @property
    def post_process_map(self) -> ProcessorMapping:
        return self._post_process_map
