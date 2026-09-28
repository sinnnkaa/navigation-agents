import enum
import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPkMixin


class AssistanceStatus(str, enum.Enum):
    CREATED = "created"
    ROUTED = "routed"
    ACCEPTED = "accepted"
    IN_SESSION = "in_session"
    CLOSED = "closed"
    ESCALATED = "escalated"


class AssistanceRequest(UUIDPkMixin, TimestampMixin, Base):
    """§8.1, §11.3, §12 ТЗ."""

    __tablename__ = "assistance_requests"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    location: Mapped[str] = mapped_column(Geography(geometry_type="POINT", srid=4326))
    agent_summary: Mapped[str | None] = mapped_column(String)
    assigned_volunteer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("volunteers.id"))
    status: Mapped[AssistanceStatus] = mapped_column(
        Enum(AssistanceStatus, name="assistance_status"), default=AssistanceStatus.CREATED
    )
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
