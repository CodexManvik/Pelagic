from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

import sqlglot
from sqlglot import exp
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class GuardResult:
    ok: bool
    reason: str | None
    tables: list[str]


@dataclass(frozen=True)
class CostResult:
    ok: bool
    cost: float | None
    reason: str | None


def validate_sql(sql: str, allowed_tables: set[str]) -> GuardResult:
    try:
        parsed = sqlglot.parse_one(sql)
    except sqlglot.errors.ParseError as exc:
        return GuardResult(False, f"SQL parse failed: {exc}", [])

    blocked_names = [
        "Delete",
        "Drop",
        "Update",
        "Insert",
        "Alter",
        "Create",
        "Truncate",
    ]
    blocked = tuple(
        getattr(exp, name) for name in blocked_names if hasattr(exp, name)
    )
    tables: set[str] = set()

    for node in parsed.walk():
        if isinstance(node, blocked):
            return GuardResult(False, "Only SELECT statements are allowed.", [])
        if isinstance(node, exp.Table):
            tables.add(node.name)

    disallowed = sorted(table for table in tables if table not in allowed_tables)
    if disallowed:
        return GuardResult(
            False,
            f"Query references disallowed tables: {', '.join(disallowed)}",
            sorted(tables),
        )

    return GuardResult(True, None, sorted(tables))


def _extract_total_cost(plan_data: Any) -> float | None:
    if isinstance(plan_data, str):
        try:
            plan_data = json.loads(plan_data)
        except json.JSONDecodeError:
            return None

    if isinstance(plan_data, dict):
        plan_data = [plan_data]

    if not isinstance(plan_data, list) or not plan_data:
        return None

    root = plan_data[0]
    plan = root.get("Plan") if isinstance(root, dict) else None
    if not isinstance(plan, dict):
        return None

    cost = plan.get("Total Cost")
    if isinstance(cost, (int, float)):
        return float(cost)
    return None


async def check_query_cost(
    session: AsyncSession,
    sql: str,
    params: dict[str, Any],
    max_cost: float,
) -> CostResult:
    sql_to_explain = sql.rstrip().rstrip(";")
    explain_sql = f"EXPLAIN (FORMAT JSON) {sql_to_explain}"

    try:
        result = await session.execute(text(explain_sql), params)
        plan_data = result.scalar_one_or_none()
    except SQLAlchemyError as exc:
        return CostResult(False, None, f"EXPLAIN failed: {exc.__class__.__name__}: {exc}")

    total_cost = _extract_total_cost(plan_data)
    if total_cost is None:
        return CostResult(True, None, None)
    if total_cost > max_cost:
        return CostResult(
            False,
            total_cost,
            f"Estimated query cost {total_cost:.2f} exceeds free-tier limit {max_cost}.",
        )

    return CostResult(True, total_cost, None)
