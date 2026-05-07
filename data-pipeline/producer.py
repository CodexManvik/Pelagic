from __future__ import annotations

import logging
import os
import random
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from qstash import QStash


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=ROOT_DIR / ".env")

MESSAGE_COUNT = 50
DEFAULT_TARGET_URL = "http://localhost:8000/api/webhooks/argo-ingest"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


logger = logging.getLogger("argo-producer")


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


def build_qstash_client() -> QStash:
    token = os.getenv("QSTASH_TOKEN")
    if not token:
        raise RuntimeError(
            "Missing QStash credential. Expected environment variable: QSTASH_TOKEN."
        )
    return QStash(token=token)


def generate_events(count: int) -> list[ArgoMeasurementEvent]:
    events: list[ArgoMeasurementEvent] = []
    now_utc = datetime.now(UTC)
    produced_at = now_utc.isoformat()
    float_id = "ARGO-7000001"

    for i in range(count):
        cycle_number = i + 1
        lat = round(random.uniform(-75.0, 75.0), 5)
        lon = round(random.uniform(-179.9, 179.9), 5)
        depth = round(random.uniform(5.0, 2000.0), 2)
        temperature = round(random.uniform(2.0, 30.0), 3)
        salinity = round(random.uniform(33.0, 37.0), 3)
        oxygen = round(random.uniform(150.0, 320.0), 2)
        profile_date = (now_utc + timedelta(hours=i)).isoformat()

        events.append(
            ArgoMeasurementEvent(
                float_id=float_id,
                cycle_number=cycle_number,
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


def main() -> None:
    configure_logging()
    client = build_qstash_client()

    target_url = os.getenv("QSTASH_TARGET_URL", DEFAULT_TARGET_URL)
    events = generate_events(MESSAGE_COUNT)
    payload = [asdict(event) for event in events]

    try:
        response = client.message.publish_json(
            url=target_url,
            body=payload,
        )
        logger.info(
            "Published %d ARGO events to QStash target=%s message_id=%s",
            len(events),
            target_url,
            response.message_id,
        )
    except Exception:
        logger.exception("Failed to publish ARGO batch to QStash.")
        raise


if __name__ == "__main__":
    main()
