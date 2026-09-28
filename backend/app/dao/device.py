import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.dao.base import BaseDAO
from app.models.user import Device


class DeviceDAO(BaseDAO):
    async def get_by_token_hash(self, token_hash: str) -> Device | None:
        return await self.session.scalar(select(Device).where(Device.token_hash == token_hash))

    async def touch_last_active(self, device: Device) -> None:
        device.last_active_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def create(self, owner_id: uuid.UUID, token_hash: str) -> Device:
        device = Device(owner_id=owner_id, token_hash=token_hash)
        self.session.add(device)
        await self.session.flush()
        return device
