from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from qstash import QStash

from argo_events import (
    DEFAULT_EVENTS_PER_PROFILE,
    DEFAULT_MESSAGE_COUNT,
    ArgoProfileHint,
    generate_events,
    generate_events_for_profiles,
    serialize_events,
)
from argo_fetcher import build_redis_client, filter_new_profiles, load_profile_hints


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=ROOT_DIR / ".env")

DEFAULT_TARGET_URL = "http://localhost:8000/api/webhooks/argo-ingest"
DEFAULT_BATCH_SIZE = 100
DEFAULT_MAX_PROFILES = 50
DEFAULT_PROFILE_CACHE_TTL_DAYS = 7
DEFAULT_PROFILE_CACHE_PREFIX = "argo:profile"
DEFAULT_INDEX_MAX_LINES = 500


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


logger = logging.getLogger("argo-producer")


def build_qstash_client() -> QStash:
    token = os.getenv("QSTASH_TOKEN")
    if not token:
        raise RuntimeError(
            "Missing QStash credential. Expected environment variable: QSTASH_TOKEN."
        )
    return QStash(token=token)


def _parse_int(value: str | None, fallback: int) -> int:
    if value is None:
        return fallback
    try:
        return max(1, int(value))
    except ValueError:
        raise RuntimeError(f"Invalid integer value: {value}")


def _chunked(items: list[dict[str, object]], size: int) -> Iterable[list[dict[str, object]]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def _load_profile_hints() -> list[ArgoProfileHint]:
    index_url = os.getenv("ARGO_INDEX_URL")
    if not index_url:
        return []

    max_profiles = _parse_int(os.getenv("ARGO_MAX_PROFILES"), DEFAULT_MAX_PROFILES)
    max_lines = _parse_int(os.getenv("ARGO_INDEX_MAX_LINES"), DEFAULT_INDEX_MAX_LINES)
    hints = load_profile_hints(
        url=index_url,
        max_profiles=max_profiles,
        max_lines=max_lines,
    )

    redis = build_redis_client()
    ttl_days = _parse_int(
        os.getenv("ARGO_PROFILE_CACHE_TTL_DAYS"), DEFAULT_PROFILE_CACHE_TTL_DAYS
    )
    key_prefix = os.getenv("ARGO_PROFILE_CACHE_PREFIX", DEFAULT_PROFILE_CACHE_PREFIX)
    ttl_seconds = ttl_days * 24 * 60 * 60
    return filter_new_profiles(hints, redis, key_prefix, ttl_seconds)


def main() -> None:
    configure_logging()
    client = build_qstash_client()

    target_url = os.getenv("QSTASH_TARGET_URL", DEFAULT_TARGET_URL)
    hints = _load_profile_hints()
    if hints:
        events_per_profile = _parse_int(
            os.getenv("ARGO_EVENTS_PER_PROFILE"),
            DEFAULT_EVENTS_PER_PROFILE,
        )
        events = generate_events_for_profiles(hints, events_per_profile)
    else:
        events = generate_events(DEFAULT_MESSAGE_COUNT)

    if not events:
        logger.warning("No ARGO events to publish.")
        return

    payload = serialize_events(events)
    batch_size = _parse_int(os.getenv("ARGO_BATCH_SIZE"), DEFAULT_BATCH_SIZE)

    try:
        for batch in _chunked(payload, batch_size):
            response = client.message.publish_json(
                url=target_url,
                body=batch,
            )
            logger.info(
                "Published %d ARGO events to QStash target=%s message_id=%s",
                len(batch),
                target_url,
                response.message_id,
            )
    except Exception:
        logger.exception("Failed to publish ARGO batch to QStash.")
        raise


if __name__ == "__main__":
    main()
