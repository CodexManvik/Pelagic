from __future__ import annotations

import logging
import random
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta

DEFAULT_MESSAGE_COUNT = 50
DEFAULT_EVENTS_PER_PROFILE = 3


logger = logging.getLogger("argo-events")


@dataclass(slots=True)
class ArgoProfileHint:
    float_id: str
    cycle_number: int
    profile_date: str | None = None
    lat: float | None = None
    lon: float | None = None


@dataclass(slots=True)
class ArgoMeasurementEvent:
    float_id: str
    cycle_number: int
    lat: float
    lon: float
    depth: float
    temperature: float
    salinity: float
    oxygen: float
    profile_date: str
    produced_at: str


def generate_events_for_profiles(
    hints: list[ArgoProfileHint],
    events_per_profile: int = DEFAULT_EVENTS_PER_PROFILE,
) -> list[ArgoMeasurementEvent]:
    events: list[ArgoMeasurementEvent] = []
    now_utc = datetime.now(UTC)
    produced_at = now_utc.isoformat()

    for hint in hints:
        lat = hint.lat if hint.lat is not None else round(random.uniform(-75.0, 75.0), 5)
        lon = hint.lon if hint.lon is not None else round(random.uniform(-179.9, 179.9), 5)
        profile_date = hint.profile_date or now_utc.isoformat()

        for i in range(events_per_profile):
            depth = round(random.uniform(5.0, 2000.0), 2)
            temperature = round(random.uniform(2.0, 30.0), 3)
            salinity = round(random.uniform(33.0, 37.0), 3)
            oxygen = round(random.uniform(150.0, 320.0), 2)

            events.append(
                ArgoMeasurementEvent(
                    float_id=hint.float_id,
                    cycle_number=hint.cycle_number,
                    lat=lat,
                    lon=lon,
                    depth=depth,
                    temperature=temperature,
                    salinity=salinity,
                    oxygen=oxygen,
                    profile_date=profile_date,
                    produced_at=produced_at,
                )
            )

    return events


def generate_events(count: int, float_id: str = "ARGO-7000001") -> list[ArgoMeasurementEvent]:
    hints = [
        ArgoProfileHint(
            float_id=float_id,
            cycle_number=index + 1,
            profile_date=(datetime.now(UTC) + timedelta(hours=index)).isoformat(),
        )
        for index in range(max(1, count))
    ]
    events_per_profile = max(1, count // max(1, len(hints)))
    return generate_events_for_profiles(hints, events_per_profile)


def serialize_events(events: list[ArgoMeasurementEvent]) -> list[dict[str, object]]:
    return [asdict(event) for event in events]
