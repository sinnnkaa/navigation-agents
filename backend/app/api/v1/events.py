import uuid
from datetime import datetime, timezone
from pathlib import Path

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, UploadFile
from geoalchemy2.elements import WKTElement

from app.api.deps import get_current_device
from app.dao.event import EventDAO
from app.models.user import Device
from app.schemas.event import EventAcceptedOut, EventBatchIn, EventBatchOut

router = APIRouter(route_class=DishkaRoute)

MEDIA_ROOT = Path(__file__).resolve().parents[3] / "data" / "media"


@router.post("/events", response_model=EventBatchOut)
async def submit_events(
    batch: EventBatchIn,
    event_dao: FromDishka[EventDAO],
    device: Device = Depends(get_current_device),
) -> EventBatchOut:
    received_at = datetime.now(timezone.utc)
    results: list[EventAcceptedOut] = []

    for item in batch.events:
        location = WKTElement(f"POINT({item.location.lon} {item.location.lat})", srid=4326)

        event_id, duplicate = await event_dao.insert_or_get_existing(
            device_id=device.id,
            client_event_id=item.client_event_id,
            kind=item.kind,
            occurred_at=item.occurred_at,
            received_at=received_at,
            location=location,
            accuracy_m=item.location.accuracy_m,
            heading=item.location.heading,
            detections=[d.model_dump(by_alias=True) for d in item.detections],
            media=item.media.model_dump(),
            battery=item.battery,
            offline_queued=item.offline_queued,
        )
        results.append(
            EventAcceptedOut(client_event_id=item.client_event_id, id=event_id, duplicate=duplicate)
        )

    await event_dao.commit()
    return EventBatchOut(results=results)


@router.post("/events/{event_id}/media", status_code=202)
async def upload_event_media(
    event_id: uuid.UUID,
    audio: UploadFile | None = None,
    frames: list[UploadFile] | None = None,
    device: Device = Depends(get_current_device),
) -> dict:
    event_dir = MEDIA_ROOT / str(event_id)
    event_dir.mkdir(parents=True, exist_ok=True)

    saved = {"audio": None, "frames": []}
    if audio is not None:
        dest = event_dir / audio.filename
        dest.write_bytes(await audio.read())
        saved["audio"] = dest.name
    for frame in frames or []:
        dest = event_dir / frame.filename
        dest.write_bytes(await frame.read())
        saved["frames"].append(dest.name)

    return {"event_id": event_id, "saved": saved}
