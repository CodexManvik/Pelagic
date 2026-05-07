from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Float, Profile
from db.session import get_db_session
from schemas.floats import FloatListResponse, FloatResponse, ProfileResponse


router = APIRouter(prefix="/api/v1", tags=["floats"])


@router.get("/floats", response_model=FloatListResponse)
async def list_floats(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
) -> FloatListResponse:
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    total = await session.scalar(select(func.count()).select_from(Float))
    result = await session.execute(
        select(Float).order_by(Float.float_id).limit(limit).offset(offset)
    )
    floats = result.scalars().all()

    return FloatListResponse(
        items=floats,
        limit=limit,
        offset=offset,
        total=total or 0,
    )


@router.get("/floats/{float_id}", response_model=FloatResponse)
async def get_float(
    float_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> FloatResponse:
    result = await session.execute(
        select(Float)
        .where(Float.float_id == float_id)
        .options(selectinload(Float.profiles).selectinload(Profile.measurements))
    )
    float_row = result.scalar_one_or_none()
    if float_row is None:
        raise HTTPException(status_code=404, detail="Float not found")

    return FloatResponse.model_validate(float_row)


@router.get("/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> ProfileResponse:
    result = await session.execute(
        select(Profile)
        .where(Profile.profile_id == profile_id)
        .options(selectinload(Profile.measurements))
    )
    profile_row = result.scalar_one_or_none()
    if profile_row is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return ProfileResponse.model_validate(profile_row)
