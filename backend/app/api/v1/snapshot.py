import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import get_current_device
from app.models.user import Device

router = APIRouter()

MEDIA_ROOT = Path(__file__).resolve().parents[3] / "data" / "media"


@router.post("/snapshot", status_code=202)
async def submit_snapshot(
    event_id: uuid.UUID,
    image: UploadFile,
    device: Device = Depends(get_current_device),
) -> dict:
    event_dir = MEDIA_ROOT / str(event_id)
    event_dir.mkdir(parents=True, exist_ok=True)
    dest = event_dir / f"snapshot_{image.filename}"
    dest.write_bytes(await image.read())

    return {"event_id": event_id, "saved": dest.name}
