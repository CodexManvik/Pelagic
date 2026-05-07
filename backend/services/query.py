from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ai.graph import build_query_graph
from core.config import get_settings
from core.logging import REQUEST_ID_CTX
from db.models import QueryAudit
from schemas.query import QueryRequest, QueryResponse


async def run_query(payload: QueryRequest, session: AsyncSession) -> QueryResponse:
    settings = get_settings()
    max_rows = payload.max_rows or settings.sql_max_rows

    graph = build_query_graph()
    result: dict[str, Any] = await graph.ainvoke(
        {
            "question": payload.question,
            "time_window_days": payload.time_window_days,
            "max_rows": max_rows,
            "router": None,
            "sql_plan": None,
            "rows": None,
            "answer": None,
            "errors": [],
            "attempt": 0,
            "session": session,
        }
    )

    if result.get("errors"):
        raise ValueError(" | ".join(result["errors"]))

    answer = result.get("answer")
    sql_plan = result.get("sql_plan")
    rows = result.get("rows") or []
    trace_id = REQUEST_ID_CTX.get("-")

    audit = QueryAudit(
        question=payload.question,
        sql=sql_plan.sql if sql_plan else None,
        answer=answer.answer if answer else None,
        confidence=answer.confidence if answer else None,
        trace_id=trace_id,
        status="ok" if answer else "error",
    )
    session.add(audit)
    await session.commit()

    return QueryResponse(
        answer=answer.answer if answer else "No answer generated.",
        sql=sql_plan.sql if sql_plan else None,
        rows=rows,
        confidence=answer.confidence if answer else None,
        trace_id=trace_id,
        notes=answer.notes if answer else [],
    )
