"""User business logic."""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from common.const import DEFAULT_PAGE_SKIP, DEFAULT_PAGE_LIMIT
from manager.user.user_manager import UserManager
from models.user import UserModel
from routers.user.request_model.user_request import (
    UserBatchUpdateItem,
    UserCreateRequest,
    UserUpdateRequest,
)
from routers.user.response_model.user_response import UserListResponse, UserResponse


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._manager = UserManager(session)

    @staticmethod
    def _to_response(user: UserModel) -> UserResponse:
        return UserResponse.model_validate(user)

    async def create_user(self, data: UserCreateRequest) -> UserResponse:
        user = await self._manager.create(
            name=data.name,
            gender=data.gender,
            hobbies=data.hobbies,
            age=data.age,
            status=data.status,
            json_extend=data.json_extend,
        )
        return self._to_response(user)

    async def get_user(self, user_id: int) -> Optional[UserResponse]:
        user = await self._manager.get_by_id(user_id)
        return self._to_response(user) if user else None

    async def update_user(self, user_id: int, data: UserUpdateRequest) -> Optional[UserResponse]:
        payload = data.model_dump(exclude_unset=True)
        user = await self._manager.update_by_id(user_id, **payload)
        return self._to_response(user) if user else None

    async def delete_user(self, user_id: int) -> bool:
        return await self._manager.delete_by_id(user_id)

    async def list_users(
        self,
        *,
        skip: int = DEFAULT_PAGE_SKIP,
        limit: int = DEFAULT_PAGE_LIMIT,
        status: Optional[int] = None,
    ) -> UserListResponse:
        total = await self._manager.count(status=status)
        rows = await self._manager.list_page(skip=skip, limit=limit, status=status)
        return UserListResponse(
            total=total,
            items=[self._to_response(u) for u in rows],
            skip=skip,
            limit=limit,
        )

    async def batch_get_users(self, ids: List[int]) -> List[UserResponse]:
        users = await self._manager.batch_get_by_ids(ids)
        return [self._to_response(u) for u in users]

    async def batch_delete_users(self, ids: List[int]) -> int:
        return await self._manager.batch_delete_by_ids(ids)

    async def batch_create_users(self, items: List[UserCreateRequest]) -> List[UserResponse]:
        dicts = [item.model_dump() for item in items]
        users = await self._manager.batch_create(dicts)
        return [self._to_response(u) for u in users]

    async def batch_update_users(self, items: List[UserBatchUpdateItem]) -> int:
        pairs: List[Tuple[int, Dict[str, Any]]] = []
        for it in items:
            data = it.model_dump(exclude={"id"}, exclude_unset=True)
            if data:
                pairs.append((it.id, data))
        return await self._manager.batch_update_by_ids(pairs)
