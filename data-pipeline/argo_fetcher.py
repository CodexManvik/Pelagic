from __future__ import annotations

import logging
import os
import re
import ssl
import urllib.request
from collections import deque
from datetime import UTC, datetime
from typing import Iterable

from upstash_redis import Redis

from argo_events import ArgoProfileHint


logger = logging.getLogger("argo-fetcher")


INDEX_FLOAT_PATTERN = re.compile(r"(?P<float>\d{5,8})_(?P<cycle>\d{3})")


def _build_ssl_context() -> ssl.SSLContext:
    skip_tls_verify = os.getenv("ARGO_SKIP_TLS_VERIFY", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if skip_tls_verify:
        logger.warning("ARGO_SKIP_TLS_VERIFY is enabled; TLS verification is disabled.")
        return ssl._create_unverified_context()

    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def build_redis_client() -> Redis | None:
    url = os.getenv("UPSTASH_REDIS_REST_URL")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    if not url or not token:
        return None
    return Redis(url=url, token=token)


def _redis_set_is_new(result: object) -> bool:
    if result is True:
        return True
    if isinstance(result, str) and result.lower() == "ok":
        return True
    if isinstance(result, int) and result == 1:
        return True
    return False


def fetch_index_lines(url: str, max_lines: int) -> list[str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "FloatChatAI/1.0"},
    )

    buffer: deque[str] = deque(maxlen=max_lines)
    context = _build_ssl_context()
    with urllib.request.urlopen(request, timeout=30, context=context) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="ignore").strip()
            if not line or line.startswith("#"):
                continue
            buffer.append(line)

    return list(buffer)


def _parse_date(value: str | None) -> str | None:
    if not value:
        return None

    text = value.strip()
    if not text.isdigit():
        return None

    try:
        if len(text) == 8:
            parsed = datetime.strptime(text, "%Y%m%d")
        elif len(text) == 14:
            parsed = datetime.strptime(text, "%Y%m%d%H%M%S")
        else:
            return None
    except ValueError:
        return None

    return parsed.replace(tzinfo=UTC).isoformat()


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_profile_hint(line: str) -> ArgoProfileHint | None:
    parts = [part.strip() for part in line.split(",") if part.strip()]
    if not parts:
        return None

    match = INDEX_FLOAT_PATTERN.search(parts[0])
    if not match:
        return None

    float_id = f"ARGO-{match.group('float')}"
    cycle_number = int(match.group("cycle"))
    profile_date = _parse_date(parts[1] if len(parts) > 1 else None)
    lat = _parse_float(parts[2] if len(parts) > 2 else None)
    lon = _parse_float(parts[3] if len(parts) > 3 else None)

    return ArgoProfileHint(
        float_id=float_id,
        cycle_number=cycle_number,
        profile_date=profile_date,
        lat=lat,
        lon=lon,
    )


def load_profile_hints(
    url: str,
    max_profiles: int,
    max_lines: int,
) -> list[ArgoProfileHint]:
    lines = fetch_index_lines(url, max_lines=max_lines)
    hints = [hint for hint in (parse_profile_hint(line) for line in lines) if hint]
    if max_profiles <= 0:
        return []
    return hints[-max_profiles:]


def filter_new_profiles(
    hints: Iterable[ArgoProfileHint],
    redis: Redis | None,
    key_prefix: str,
    ttl_seconds: int,
) -> list[ArgoProfileHint]:
    if not redis:
        return list(hints)

    deduped: list[ArgoProfileHint] = []
    for hint in hints:
        key = f"{key_prefix}:{hint.float_id}:{hint.cycle_number}"
        try:
            result = redis.set(key, "1", ex=ttl_seconds, nx=True)
        except Exception:
            logger.exception("Failed to update Redis checkpoint; returning all hints.")
            return list(hints)

        if _redis_set_is_new(result):
            deduped.append(hint)

    return deduped
