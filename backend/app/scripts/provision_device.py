"""Регистрация устройства вне API (§7.1 ТЗ не описывает сам процесс выдачи

токена). Используется для тестов и симулятора.

Запуск: python -m app.scripts.provision_device
"""

import asyncio

from app.core.database import async_session_factory
from app.core.security import generate_device_token
from app.dao.device import DeviceDAO
from app.dao.user import UserDAO
from app.models.user import UserRole


async def main() -> None:
    raw_token, token_hash = generate_device_token()

    async with async_session_factory() as session:
        user_dao = UserDAO(session)
        device_dao = DeviceDAO(session)

        user = await user_dao.create(role=UserRole.BLIND_USER)
        device = await device_dao.create(owner_id=user.id, token_hash=token_hash)
        await session.commit()
        await session.refresh(device)

        print(f"user_id={user.id}")
        print(f"device_id={device.id}")
        print(f"token={raw_token}")


if __name__ == "__main__":
    asyncio.run(main())
