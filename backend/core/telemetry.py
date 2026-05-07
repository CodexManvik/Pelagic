from __future__ import annotations

from typing import Any

from prometheus_fastapi_instrumentator import Instrumentator


def configure_metrics(app: Any) -> None:
    Instrumentator().instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
    )
