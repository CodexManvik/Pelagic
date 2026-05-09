import logging
from contextvars import ContextVar
from typing import Final

REQUEST_ID_CTX: Final[ContextVar[str]] = ContextVar("request_id", default="-")
_ORIGINAL_FACTORY = logging.getLogRecordFactory()


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = REQUEST_ID_CTX.get("-")
        return True


def _record_factory(*args, **kwargs) -> logging.LogRecord:
    record = _ORIGINAL_FACTORY(*args, **kwargs)
    if not hasattr(record, "request_id"):
        record.request_id = REQUEST_ID_CTX.get("-")
    return record


def configure_logging(level: str = "INFO") -> None:
    logging.setLogRecordFactory(_record_factory)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(request_id)s | %(message)s",
    )
    logging.getLogger().addFilter(RequestIdFilter())
