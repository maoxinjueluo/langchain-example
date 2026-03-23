"""User HTTP routes."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from common.const import (
    USER_ROUTER_PREFIX,
    USER_ROUTER_TAG,
    DEFAULT_PAGE_SKIP,
    DEFAULT_PAGE_LIMIT,
    MAX_PAGE_LIMIT,
    MESSAGE_DELETED,
    MESSAGE_BATCH_DELETED,
    MESSAGE_BATCH_UPDATED,
    USER_NOT_FOUND,
)
from database import get_session
from routers.user.request_model.user_request import (
    UserBatchCreateRequest,
    UserBatchDeleteRequest,
    UserBatchGetRequest,
    UserBatchUpdateRequest,
    UserCreateRequest,
    UserUpdateRequest,
)
from routers.user.response_model.user_response import MessageResponse, UserListResponse, UserResponse
from services.user.user_service import UserService

router = APIRouter(prefix=USER_ROUTER_PREFIX, tags=[USER_ROUTER_TAG])


async def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreateRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.create_user(body)


@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = Query(DEFAULT_PAGE_SKIP, ge=0),
    limit: int = Query(DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT),
    status_filter: Optional[int] = Query(None, alias="status"),
    service: UserService = Depends(get_user_service),
) -> UserListResponse:
    return await service.list_users(skip=skip, limit=limit, status=status_filter)


@router.post("/batch/query", response_model=List[UserResponse])
async def batch_get_users(
    body: UserBatchGetRequest,
    service: UserService = Depends(get_user_service),
) -> List[UserResponse]:
    return await service.batch_get_users(body.ids)


@router.post("/batch", response_model=List[UserResponse], status_code=status.HTTP_201_CREATED)
async def batch_create_users(
    body: UserBatchCreateRequest,
    service: UserService = Depends(get_user_service),
) -> List[UserResponse]:
    return await service.batch_create_users(body.items)


@router.delete("/batch", response_model=MessageResponse)
async def batch_delete_users(
    body: UserBatchDeleteRequest,
    service: UserService = Depends(get_user_service),
) -> MessageResponse:
    n = await service.batch_delete_users(body.ids)
    return MessageResponse(message=MESSAGE_BATCH_DELETED, affected=n)


@router.patch("/batch", response_model=MessageResponse)
async def batch_update_users(
    body: UserBatchUpdateRequest,
    service: UserService = Depends(get_user_service),
) -> MessageResponse:
    n = await service.batch_update_users(body.items)
    return MessageResponse(message=MESSAGE_BATCH_UPDATED, affected=n)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    body: UserUpdateRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await service.update_user(user_id, body)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)
    return user


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> MessageResponse:
    ok = await service.delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)
    return MessageResponse(message=MESSAGE_DELETED, affected=1)
