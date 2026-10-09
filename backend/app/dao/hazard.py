from datetime import datetime

from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_X, ST_Y, ST_MakeEnvelope
from sqlalchemy import Row, cast, select

from app.dao.base import BaseDAO
from app.models.hazard import Hazard


class HazardDAO(BaseDAO):
    async def list_in_bbox(
        self,
        bbox: tuple[float, float, float, float] | None = None,
        since: datetime | None = None,
    ) -> list[Row[tuple[Hazard, float, float]]]:
        geom = cast(Hazard.location, Geometry)
        stmt = select(Hazard, ST_X(geom), ST_Y(geom))

        if bbox:
            west, south, east, north = bbox
            envelope = ST_MakeEnvelope(west, south, east, north, 4326)
            stmt = stmt.where(Hazard.location.intersects(envelope))

        if since:
            stmt = stmt.where(Hazard.created_at >= since)

        return (await self.session.execute(stmt)).all()
