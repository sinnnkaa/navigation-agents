import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPkMixin


class UserRole(str, enum.Enum):
    BLIND_USER = "blind_user"
    VOLUNTEER = "volunteer"
    ADMIN = "admin"


class User(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "users"

    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"))
    language: Mapped[str] = mapped_column(String(8), default="ru")
    # §8.1: подробность подсказок, темп речи и др.
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)

    devices: Mapped[list["Device"]] = relationship(back_populates="owner")


class Device(UUIDPkMixin, Base):
    __tablename__ = "devices"

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    firmware_version: Mapped[str | None] = mapped_column(String(32))
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    owner: Mapped["User"] = relationship(back_populates="devices")
