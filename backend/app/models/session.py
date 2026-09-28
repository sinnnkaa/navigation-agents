import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPkMixin


class Session(UUIDPkMixin, TimestampMixin, Base):
    """§8.1, §12 ТЗ. Видеосессия пользователя с волонтёром."""

    __tablename__ = "sessions"

    request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assistance_requests.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # список участников: [{"user_id": ..., "role": "blind_user" | "volunteer"}]
    participants: Mapped[list] = mapped_column(JSONB, default=list)
    snapshots_count: Mapped[int] = mapped_column(Integer, default=0)
