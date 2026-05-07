from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    time_window_days: int | None = Field(default=None, ge=1, le=365)
    max_rows: int | None = Field(default=None, ge=1, le=5000)


class QueryResponse(BaseModel):
    answer: str
    sql: str | None = None
    rows: list[dict[str, Any]]
    confidence: float | None = None
    trace_id: str | None = None
    notes: list[str] = []
