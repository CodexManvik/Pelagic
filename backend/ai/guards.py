from __future__ import annotations

from dataclasses import dataclass

import sqlglot
from sqlglot import exp


@dataclass(frozen=True)
class GuardResult:
    ok: bool
    reason: str | None
    tables: list[str]


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
