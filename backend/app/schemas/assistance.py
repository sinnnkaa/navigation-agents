import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.assistance import AssistanceStatus


class AssistanceRequestIn(BaseModel):
    lat: float
    lon: float
    note: str | None = None


class AssistanceRequestOut(BaseModel):
    id: uuid.UUID
    status: AssistanceStatus
    created_at: datetime
