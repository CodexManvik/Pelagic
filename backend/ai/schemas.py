from typing import Any, Literal

from pydantic import BaseModel, Field


class RouterDecision(BaseModel):
    intent: Literal["profile_lookup", "aggregation", "summary", "unknown"]
    tables: list[str] = Field(default_factory=list)
    requires_time_window: bool = False
    notes: str | None = None


class SqlPlan(BaseModel):
    sql: str
    params: dict[str, Any] = Field(default_factory=dict)
    rationale: str | None = None


class OceanographerAnswer(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    notes: list[str] = Field(default_factory=list)
