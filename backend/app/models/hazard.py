import enum
import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPkMixin


class HazardStatus(str, enum.Enum):
    UNCONFIRMED = "unconfirmed"
    CONFIRMED = "confirmed"
    MODERATION = "moderation"
    ARCHIVED = "archived"


class HazardSource(str, enum.Enum):
    AGENT = "agent"
    MODERATOR = "moderator"


class Hazard(UUIDPkMixin, TimestampMixin, Base):
    """§8.1, §8.2 ТЗ. Тип — из 19 классов детектора + пользовательские, свободной строкой."""

    __tablename__ = "hazards"

    type: Mapped[str] = mapped_column(String(64), index=True)
    location: Mapped[str] = mapped_column(Geography(geometry_type="POINT", srid=4326))
    influence_radius_m: Mapped[float] = mapped_column(Float, default=5.0)

    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[HazardStatus] = mapped_column(
        Enum(HazardStatus, name="hazard_status"), default=HazardStatus.UNCONFIRMED
    )

    first_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    confirmations_count: Mapped[int] = mapped_column(Integer, default=0)
    refutations_count: Mapped[int] = mapped_column(Integer, default=0)

    source: Mapped[HazardSource] = mapped_column(Enum(HazardSource, name="hazard_source"))


class HazardEventRelation(str, enum.Enum):
    CONFIRMS = "confirms"
    REFUTES = "refutes"


class HazardEvent(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "hazard_events"

    hazard_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hazards.id"))
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id"))
    relation: Mapped[HazardEventRelation] = mapped_column(
        Enum(HazardEventRelation, name="hazard_event_relation")
    )
