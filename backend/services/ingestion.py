from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from db.models import Float, Measurement, Profile
from schemas.ingestion import ArgoMeasurementPayload
from upstash_redis import Redis


logger = logging.getLogger("argo-ingestion")


def decode_payload(raw_body: str) -> list[ArgoMeasurementPayload]:
    parsed = json.loads(raw_body)

    if not isinstance(parsed, list):
        raise ValueError("Payload must be a JSON list of objects.")

    records = [item for item in parsed if isinstance(item, dict)]
    if len(records) != len(parsed):
        raise ValueError("All payload items must be JSON objects.")

    return [ArgoMeasurementPayload.model_validate(record) for record in records]


def dedupe_measurements(
    events: list[ArgoMeasurementPayload],
) -> list[ArgoMeasurementPayload]:
    deduped: dict[tuple[str, int, float], ArgoMeasurementPayload] = {}
    for event in events:
        key = (event.float_id, event.cycle_number, event.depth)
        deduped[key] = event
    return list(deduped.values())


def _build_redis_client() -> Redis | None:
    settings = get_settings()
    if not settings.upstash_redis_rest_url or not settings.upstash_redis_rest_token:
        return None
    return Redis(
        url=settings.upstash_redis_rest_url,
        token=settings.upstash_redis_rest_token,
    )


def _redis_set_is_new(result: object) -> bool:
    if result is True:
        return True
    if isinstance(result, str) and result.lower() == "ok":
        return True
    if isinstance(result, int) and result == 1:
        return True
    return False


async def _dedupe_with_redis(
    events: list[ArgoMeasurementPayload],
) -> list[ArgoMeasurementPayload]:
    redis = _build_redis_client()
    if not redis:
        return events

    settings = get_settings()
    ttl_seconds = max(1, settings.measurement_ttl_days) * 24 * 60 * 60
    deduped: list[ArgoMeasurementPayload] = []

    for event in events:
        key = f"argo:dedupe:{event.float_id}:{event.cycle_number}:{event.depth}"
        try:
            result = await asyncio.to_thread(
                redis.set,
                key,
                "1",
                ex=ttl_seconds,
                nx=True,
            )
        except Exception:
            logger.exception("Redis dedupe failed; proceeding without cache.")
            return events

        if _redis_set_is_new(result):
            deduped.append(event)

    return deduped


async def persist_events(
    session: AsyncSession,
    events: list[ArgoMeasurementPayload],
) -> None:
    if not events:
        return

    deduped_events = dedupe_measurements(events)
    deduped_events = await _dedupe_with_redis(deduped_events)
    if not deduped_events:
        return
    now_utc = datetime.now(UTC)

    float_rows_by_id: dict[str, dict[str, Any]] = {}
    for event in deduped_events:
        float_rows_by_id[event.float_id] = {
            "float_id": event.float_id,
            "wmo_id": event.float_id.replace("ARGO-", ""),
            "deployment_date": (event.profile_date or now_utc).date(),
        }

    float_rows = list(float_rows_by_id.values())
    if float_rows:
        float_insert = pg_insert(Float).values(float_rows)
        float_upsert = float_insert.on_conflict_do_update(
            index_elements=[Float.float_id],
            set_={
                "wmo_id": float_insert.excluded.wmo_id,
                "deployment_date": float_insert.excluded.deployment_date,
            },
        )
        await session.execute(float_upsert)

    profile_rows = [
        {
            "float_id": event.float_id,
            "cycle_number": event.cycle_number,
            "profile_date": event.profile_date or now_utc,
            "lat": event.lat,
            "lon": event.lon,
        }
        for event in deduped_events
    ]

    profile_insert = pg_insert(Profile).values(profile_rows)
    profile_upsert = profile_insert.on_conflict_do_update(
        index_elements=[Profile.float_id, Profile.cycle_number],
        set_={
            "profile_date": profile_insert.excluded.profile_date,
            "lat": profile_insert.excluded.lat,
            "lon": profile_insert.excluded.lon,
        },
    ).returning(
        Profile.profile_id,
        Profile.float_id,
        Profile.cycle_number,
    )
    profile_result = await session.execute(profile_upsert)
    profile_rows_returned = profile_result.mappings().all()
    profile_id_by_key = {
        (row["float_id"], row["cycle_number"]): row["profile_id"]
        for row in profile_rows_returned
    }

    measurement_rows = [
        {
            "profile_id": profile_id_by_key[(event.float_id, event.cycle_number)],
            "depth": event.depth,
            "temperature": event.temperature,
            "salinity": event.salinity,
            "oxygen": event.oxygen,
        }
        for event in deduped_events
    ]

    if measurement_rows:
        measurement_insert = pg_insert(Measurement).values(measurement_rows)
        measurement_upsert = measurement_insert.on_conflict_do_update(
            index_elements=[Measurement.profile_id, Measurement.depth],
            set_={
                "temperature": measurement_insert.excluded.temperature,
                "salinity": measurement_insert.excluded.salinity,
                "oxygen": measurement_insert.excluded.oxygen,
            },
        )
        await session.execute(measurement_upsert)
