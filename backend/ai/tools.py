from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


SCHEMA_CONTEXT = """
Tables:
- floats(float_id, wmo_id, deployment_date)
- profiles(profile_id, float_id, cycle_number, profile_date, lat, lon)
- measurements(id, profile_id, depth, temperature, salinity, oxygen)

Relationships:
- profiles.float_id -> floats.float_id
- measurements.profile_id -> profiles.profile_id

Notes:
- profile_date lives on profiles; join profiles when filtering by time.
""".strip()


def apply_row_limit(sql: str, limit: int) -> tuple[str, dict[str, Any]]:
    lowered = sql.lower()
    if "limit" in lowered:
        return sql, {}

    trimmed = sql.rstrip().rstrip(";")
    limited_sql = f"SELECT * FROM ({trimmed}) AS limited_query LIMIT :_limit"
    return limited_sql, {"_limit": limit}


async def execute_sql(
    session: AsyncSession,
    sql: str,
    params: dict[str, Any],
    max_rows: int,
) -> list[dict[str, Any]]:
    sql_to_run, extra_params = apply_row_limit(sql, max_rows)
    final_params = {**params, **extra_params}
    result = await session.execute(text(sql_to_run), final_params)
    return [dict(row) for row in result.mappings().all()]
