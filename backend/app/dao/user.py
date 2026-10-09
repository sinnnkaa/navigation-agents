from app.dao.base import BaseDAO
from app.models.user import User, UserRole


class UserDAO(BaseDAO):
    async def create(self, role: UserRole) -> User:
        user = User(role=role)
        self.session.add(user)
        await self.session.flush()
        return user
