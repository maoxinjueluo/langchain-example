from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from common.security import decode_access_token
from database import get_session
from models.auth import User


async def get_current_user_optional(
    session: AsyncSession = Depends(get_session),
    access_token: Optional[str] = Cookie(default=None),
) -> Optional[User]:
    if not access_token:
        return None
    payload = decode_access_token(access_token)
    user_id = payload.get("sub")
    if not user_id:
        return None
    result = await session.execute(select(User).where(User.id == str(user_id)))
    return result.scalar_one_or_none()


async def require_user(user: Optional[User] = Depends(get_current_user_optional)) -> User:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    return user


async def require_admin(user: User = Depends(require_user)) -> User:
    if user.role not in {"admin", "superadmin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    return user
