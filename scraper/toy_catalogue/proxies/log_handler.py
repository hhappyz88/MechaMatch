import logging
from collections import deque
import threading
from typing import Deque


class BufferingLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.buffer: Deque[logging.LogRecord] = deque()
        self.lock: threading.Lock = threading.Lock()

    def emit(self, record) -> None:
        with self.lock:
            self.buffer.append(record)

    def flush_to(self, target_logger: logging.Logger) -> None:
        with self.lock:
            for record in self.buffer:
                target_logger.handle(record)
            self.buffer.clear()


# @contextmanager
# def mute_all_logs():
#     # Save logger state
#     loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
#     loggers.append(logging.getLogger())  # Include root logger

#     saved_levels = {logger.name: logger.level for logger in loggers}
#     saved_handlers = {logger.name: list(logger.handlers) for logger in loggers}

#     try:
#         # Mute all
#         for logger in loggers:
#             logger.setLevel(logging.CRITICAL)
#             logger.handlers = []
#         yield
#     finally:
#         # Restore all
#         for logger in loggers:
#             if logger.name in saved_levels:
#                 logger.setLevel(saved_levels[logger.name])
#             if logger.name in saved_handlers:
#                 logger.handlers = saved_handlers[logger.name]
