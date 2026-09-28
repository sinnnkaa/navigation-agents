import uuid
from datetime import datetime

from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.dao.base import BaseDAO
from app.models.event import Event


class EventDAO(BaseDAO):
    async def insert_or_get_existing(
        self,
        *,
        device_id: uuid.UUID,
        client_event_id: uuid.UUID,
        kind: str,
        occurred_at: datetime,
        received_at: datetime,
        location: WKTElement,
        accuracy_m: float,
        heading: float,
        detections: list[dict],
        media: dict,
        battery: int,
        offline_queued: bool,
    ) -> tuple[uuid.UUID, bool]:
        """Вставляет событие; при конфликте (device_id, client_event_id) возвращает id уже существующей записи."""
        stmt = (
            pg_insert(Event)
            .values(
                client_event_id=client_event_id,
                device_id=device_id,
                kind=kind,
                occurred_at=occurred_at,
                received_at=received_at,
                location=location,
                accuracy_m=accuracy_m,
                heading=heading,
                detections=detections,
                media=media,
                battery=battery,
                offline_queued=offline_queued,
            )
            .on_conflict_do_nothing(index_elements=["device_id", "client_event_id"])
            .returning(Event.id)
        )
        inserted_id = await self.session.scalar(stmt)
        if inserted_id is not None:
            return inserted_id, False

        existing_id = await self.session.scalar(
            select(Event.id).where(
                Event.device_id == device_id, Event.client_event_id == client_event_id
            )
        )
        return existing_id, True
