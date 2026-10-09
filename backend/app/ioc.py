"""Провайдеры Dishka: сессия БД на запрос + DAO поверх неё."""

from collections.abc import AsyncIterable

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.dao.assistance import AssistanceDAO
from app.dao.device import DeviceDAO
from app.dao.event import EventDAO
from app.dao.hazard import HazardDAO
from app.dao.user import UserDAO


class RequestProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_session(self) -> AsyncIterable[AsyncSession]:
        async with async_session_factory() as session:
            yield session

    device_dao = provide(DeviceDAO)
    user_dao = provide(UserDAO)
    event_dao = provide(EventDAO)
    hazard_dao = provide(HazardDAO)
    assistance_dao = provide(AssistanceDAO)


def build_container() -> AsyncContainer:
    return make_async_container(RequestProvider())
