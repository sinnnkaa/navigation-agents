from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import hash_token
from app.dao.device import DeviceDAO
from app.models.user import Device

bearer_scheme = HTTPBearer(auto_error=False)


@inject
async def get_current_device(
    device_dao: FromDishka[DeviceDAO],
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Device:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")

    token_hash = hash_token(credentials.credentials)
    device = await device_dao.get_by_token_hash(token_hash)

    if device is None or device.revoked_at is not None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or revoked device token")

    await device_dao.touch_last_active(device)
    return device
