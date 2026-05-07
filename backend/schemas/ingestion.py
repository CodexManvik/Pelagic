from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArgoMeasurementPayload(BaseModel):
    float_id: str
    cycle_number: int
    lat: float
    lon: float
    depth: float
    temperature: float | None = None
    salinity: float | None = None
    oxygen: float | None = None
    profile_date: datetime | None = None
    produced_at: str | None = None

    model_config = ConfigDict(extra="ignore")
