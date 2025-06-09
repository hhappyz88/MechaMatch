from __future__ import annotations
import json
from datetime import datetime, timezone
from shared_types.session import LogEntry
from threading import Lock
from typing import Any, TYPE_CHECKING
from pathlib import Path
import logging

if TYPE_CHECKING:
    from moduscrape.runtime.registry import ServiceRegistry


class SessionLogger:
    _registry: ServiceRegistry
    _flushed_index: int
    _logs: list[LogEntry] = []
    _lock: Lock

    def __init__(self, registry: ServiceRegistry) -> None:
        self._registry = registry
        self._flushed_index = 0
        self._logs = []
        self._lock = Lock()

    def record_event(
        self, event_type: str, source: str, details: dict[str, Any]
    ) -> None:
        entry: LogEntry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "source": source,
            "details": details,
        }

        with self._lock:
            self._logs.append(entry)

    def record_success(self, source: str, msg: str, extra: dict[str, Any] = {}) -> None:
        self.record_event("success", source, {"message": msg, **extra})

    def record_error(self, source: str, msg: str, error: Exception | str) -> None:
        self.record_event(
            "error",
            source,
            {
                "message": msg,
                "error": repr(error) if isinstance(error, Exception) else error,
            },
        )

    def flush_events_to_file(self) -> None:
        """
        Flush current logs to file. File path is resolved via registry's context.
        """
        with self._lock:
            if not self._logs:
                return

            path: Path = self._registry.session_dir / "events.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)

            with path.open("a", encoding="utf-8") as f:
                for event in self._logs:
                    f.write(json.dumps(event) + "\n")

            self._logs.clear()

    def flush_events_to_backend(self) -> None:
        """
        Optional: Send logs to backend. Use callback system or in-memory queues.
        """
        with self._lock:
            if not self._logs:
                return

            # TODO: callback = self._registry.live_log_callback
            # if callback is not None:
            #     for event in self._logs:
            #         callback(event)

            self._logs.clear()

    def flush_all(self) -> None:
        """
        Full flush. Combine file + backend if needed.
        """
        self.flush_events_to_file()
        self.flush_events_to_backend()


class SessionLoggerMixin:
    registry: ServiceRegistry

    @property
    def logger(self) -> SessionLogger:
        return self.registry.logger

    def log_success(self, source: str, msg: str, extra: dict[str, Any] = {}) -> None:
        self.logger.record_success(source, msg, extra)

    def log_error(self, source: str, msg: str, err: Exception | str) -> None:
        self.logger.record_error(source, msg, err)

    def log_event(self, event_type: str, source: str, details: dict[str, Any]) -> None:
        self.logger.record_event(event_type, source, details)


class SessionLoggerAdapter(logging.Handler):
    def __init__(self, session_logger: SessionLogger) -> None:
        super().__init__()
        self.session_logger = session_logger

    def emit(self, record: logging.LogRecord) -> None:
        self.session_logger.record_event(
            event_type="log",
            source=record.name,
            details={
                "level": record.levelname,
                "message": self.format(record),
                "pathname": record.pathname,
                "lineno": record.lineno,
                "funcName": record.funcName,
                "timestamp": record.created,
            },
        )
