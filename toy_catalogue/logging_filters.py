import logging


class HTTP429Filter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "429" in record.getMessage()
