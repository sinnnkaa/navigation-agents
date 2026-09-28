from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends
from geoalchemy2.elements import WKTElement

from app.api.deps import get_current_device
from app.dao.assistance import AssistanceDAO
from app.models.user import Device
from app.schemas.assistance import AssistanceRequestIn, AssistanceRequestOut

router = APIRouter(route_class=DishkaRoute)


@router.post("/assistance", response_model=AssistanceRequestOut, status_code=201)
async def create_assistance_request(
    payload: AssistanceRequestIn,
    assistance_dao: FromDishka[AssistanceDAO],
    device: Device = Depends(get_current_device),
) -> AssistanceRequestOut:
    location = WKTElement(f"POINT({payload.lon} {payload.lat})", srid=4326)
    request = await assistance_dao.create(
        user_id=device.owner_id, location=location, note=payload.note
    )
    return AssistanceRequestOut(id=request.id, status=request.status, created_at=request.created_at)
