import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.hazard import HazardStatus


class HazardOut(BaseModel):
    id: uuid.UUID
    type: str
    lat: float
    lon: float
    influence_radius_m: float
    confidence: float
    status: HazardStatus
    confirmations_count: int
    refutations_count: int
    first_confirmed_at: datetime | None
    last_confirmed_at: datetime | None
