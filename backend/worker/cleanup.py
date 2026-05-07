from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select

from core.config import get_settings
from db.models import Measurement, Profile
from db.session import AsyncSessionLocal


async def run_cleanup(days: int | None = None) -> None:
    settings = get_settings()
    ttl_days = days or settings.measurement_ttl_days
    cutoff = datetime.now(UTC) - timedelta(days=ttl_days)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            profile_ids = select(Profile.profile_id).where(Profile.profile_date < cutoff)
            await session.execute(
                delete(Measurement).where(Measurement.profile_id.in_(profile_ids))
            )
            await session.execute(delete(Profile).where(Profile.profile_date < cutoff))
