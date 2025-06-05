import logging
from datetime import datetime, timezone
from typing import Any
from .session_manager import SessionContext


class SessionLoggingHandler(logging.Handler):
    def __init__(self, session_context: SessionContext) -> None:
        super().__init__()
        self.session_context = session_context

    def emit(self, record: logging.LogRecord) -> None:
        try:
            # Format the message (you can customize the formatter if needed)
            msg = self.format(record)
            # Timestamp as ISO string (UTC)
            timestamp = datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat()

            # Build structured event
            event: dict[str, Any] = {
                "message": msg,
                "logger_name": record.name,
                "pathname": record.pathname,
                "lineno": record.lineno,
                "funcName": record.funcName,
                "thread": record.threadName,
                "process": record.processName,
                "timestamp": timestamp,
            }

            # Use levelname as event_type, e.g. "INFO", "ERROR"
            event_type = record.levelname

            # Report event to session context
            self.session_context.record_event(
                event_type=event_type,
                source=record.name or "scrapy",
                details=event,
            )
        except Exception:
            self.handleError(record)
