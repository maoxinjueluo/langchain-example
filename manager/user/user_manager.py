"""User table async data access."""

from sqlalchemy.ext.asyncio import AsyncSession

from manager.base import BaseManager
from models.user import UserModel


class UserManager(BaseManager[UserModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserModel)
