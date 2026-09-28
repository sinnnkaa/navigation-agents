import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.event import EventKind


class EventLocationIn(BaseModel):
    lat: float
    lon: float
    accuracy_m: float | None = None
    heading: float | None = None


class EventDetectionIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_name: str = Field(alias="class")
    conf: float
    bbox: list[float]
    distance_m: float | None = None


class EventMediaIn(BaseModel):
    audio: str | None = None
    frames: list[str] = Field(default_factory=list)


class EventIn(BaseModel):
    """§7.3 ТЗ. device_id — идентификатор устройства (UUID), совпадающий с

    аутентифицированным по токену устройством; при расхождении событие отклоняется.
    """

    client_event_id: uuid.UUID
    device_id: uuid.UUID
    kind: EventKind
    occurred_at: datetime
    location: EventLocationIn
    detections: list[EventDetectionIn] = Field(default_factory=list)
    media: EventMediaIn = Field(default_factory=EventMediaIn)
    battery: int | None = None
    offline_queued: bool = False


class EventBatchIn(BaseModel):
    events: list[EventIn]


class EventAcceptedOut(BaseModel):
    client_event_id: uuid.UUID
    id: uuid.UUID
    duplicate: bool


class EventBatchOut(BaseModel):
    results: list[EventAcceptedOut]
