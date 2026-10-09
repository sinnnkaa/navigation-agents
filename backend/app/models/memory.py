import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPkMixin


class DialogRole(str, enum.Enum):
    USER = "user"
    AGENT = "agent"


class UserMemory(UUIDPkMixin, TimestampMixin, Base):
    """§8.1, §10.1 ТЗ. Долговременная память о пользователе."""

    __tablename__ = "user_memories"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String(64))
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DialogTurn(UUIDPkMixin, Base):
    """§8.1, §10.1 ТЗ. Эпизодическая память — история диалога."""

    __tablename__ = "dialog_turns"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    role: Mapped[DialogRole] = mapped_column(Enum(DialogRole, name="dialog_role"))
    content: Mapped[str] = mapped_column(String)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_compressed: Mapped[bool] = mapped_column(Boolean, default=False)
    summary_of_turn_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("dialog_turns.id"))
