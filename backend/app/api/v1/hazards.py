from datetime import datetime

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_device
from app.dao.hazard import HazardDAO
from app.models.user import Device
from app.schemas.hazard import HazardOut

router = APIRouter(route_class=DishkaRoute)


@router.get("/hazards", response_model=list[HazardOut])
async def list_hazards(
    hazard_dao: FromDishka[HazardDAO],
    bbox: str | None = Query(None, description="west,south,east,north"),
    since: datetime | None = None,
    device: Device = Depends(get_current_device),
) -> list[HazardOut]:
    bbox_tuple = tuple(float(v) for v in bbox.split(",")) if bbox else None
    rows = await hazard_dao.list_in_bbox(bbox_tuple, since)
    return [
        HazardOut(
            id=h.id,
            type=h.type,
            lon=lon,
            lat=lat,
            influence_radius_m=h.influence_radius_m,
            confidence=h.confidence,
            status=h.status,
            confirmations_count=h.confirmations_count,
            refutations_count=h.refutations_count,
            first_confirmed_at=h.first_confirmed_at,
            last_confirmed_at=h.last_confirmed_at,
        )
        for h, lon, lat in rows
    ]
