from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MeasurementResponse(BaseModel):
    id: int
    depth: float
    temperature: float | None
    salinity: float | None
    oxygen: float | None

    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    profile_id: int
    float_id: str
    cycle_number: int
    profile_date: datetime | None
    lat: float | None
    lon: float | None
    measurements: list[MeasurementResponse]

    model_config = ConfigDict(from_attributes=True)


class FloatResponse(BaseModel):
    float_id: str
    wmo_id: str | None
    deployment_date: date | None
    profiles: list[ProfileResponse]

    model_config = ConfigDict(from_attributes=True)


class FloatSummaryResponse(BaseModel):
    float_id: str
    wmo_id: str | None
    deployment_date: date | None

    model_config = ConfigDict(from_attributes=True)


class FloatListResponse(BaseModel):
    items: list[FloatSummaryResponse]
    limit: int = Field(ge=1, le=200)
    offset: int = Field(ge=0)
    total: int
