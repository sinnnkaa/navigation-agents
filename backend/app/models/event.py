import enum
import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPkMixin


class EventKind(str, enum.Enum):
    VOICE_REPORT = "voice_report"
    AUTO_DETECTION = "auto_detection"
    ASSISTANCE = "assistance"


class EventProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    ERROR = "error"


class Event(UUIDPkMixin, TimestampMixin, Base):
    """§8.1, §7.3 ТЗ. Дедупликация — по паре (device_id, client_event_id)."""

    __tablename__ = "events"
    __table_args__ = (UniqueConstraint("device_id", "client_event_id", name="uq_device_client_event"),)

    client_event_id: Mapped[uuid.UUID]
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"))
    kind: Mapped[EventKind] = mapped_column(Enum(EventKind, name="event_kind"))

    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    location: Mapped[str] = mapped_column(Geography(geometry_type="POINT", srid=4326))
    accuracy_m: Mapped[float | None] = mapped_column(Float)
    heading: Mapped[float | None] = mapped_column(Float)

    detections: Mapped[list] = mapped_column(JSONB, default=list)
    media: Mapped[dict] = mapped_column(JSONB, default=dict)
    transcript: Mapped[str | None] = mapped_column(String)

    battery: Mapped[int | None] = mapped_column(Integer)
    offline_queued: Mapped[bool] = mapped_column(default=False)

    processing_status: Mapped[EventProcessingStatus] = mapped_column(
        Enum(EventProcessingStatus, name="event_processing_status"),
        default=EventProcessingStatus.PENDING,
    )
