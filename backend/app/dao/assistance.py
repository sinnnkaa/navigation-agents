import uuid

from geoalchemy2.elements import WKTElement

from app.dao.base import BaseDAO
from app.models.assistance import AssistanceRequest


class AssistanceDAO(BaseDAO):
    async def create(
        self, *, user_id: uuid.UUID, location: WKTElement, note: str | None
    ) -> AssistanceRequest:
        request = AssistanceRequest(user_id=user_id, location=location, agent_summary=note)
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request
