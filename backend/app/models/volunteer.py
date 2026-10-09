import enum
import uuid

from sqlalchemy import ARRAY, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPkMixin


class VolunteerStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


class Volunteer(UUIDPkMixin, TimestampMixin, Base):
    """§8.1, §3 ТЗ."""

    __tablename__ = "volunteers"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    languages: Mapped[list[str]] = mapped_column(ARRAY(String(8)), default=list)
    districts: Mapped[list[str]] = mapped_column(ARRAY(String(64)), default=list)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String(64)), default=list)
    availability_schedule: Mapped[dict] = mapped_column(JSONB, default=dict)
    current_status: Mapped[VolunteerStatus] = mapped_column(
        Enum(VolunteerStatus, name="volunteer_status"), default=VolunteerStatus.OFFLINE
    )
    # §11.3: статистика откликов для агента-маршрутизатора
    response_stats: Mapped[dict] = mapped_column(JSONB, default=dict)
