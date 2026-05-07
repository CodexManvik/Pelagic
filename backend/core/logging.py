import logging
from contextvars import ContextVar
from typing import Final

REQUEST_ID_CTX: Final[ContextVar[str]] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = REQUEST_ID_CTX.get("-")
        return True


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(request_id)s | %(message)s",
    )
    logging.getLogger().addFilter(RequestIdFilter())
