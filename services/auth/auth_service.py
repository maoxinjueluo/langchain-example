from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from common.mailer import send_email
from common.security import hash_password, token_hash, token_urlsafe, verify_password
from common.settings import get_settings
from common.const import UserRole
from models.auth import EmailVerificationToken, PasswordResetToken, User, UserSession


def _password_ok(password: str) -> bool:
    if len(password) < 8:
        return False
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_letter and has_digit


class AuthService:
    @staticmethod
    def _is_expired(dt: datetime) -> bool:
        if dt.tzinfo is None:
            return dt < datetime.utcnow()
        return dt < datetime.now(timezone.utc)

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def create_user(self, *, email: str, name: str, password: str) -> User:
        email = email.lower().strip()
        if not _password_ok(password):
            raise ValueError("密码强度不足")
        exists = await self.get_user_by_email(email)
        if exists:
            raise ValueError("邮箱已注册")

        total = (await self._session.execute(select(User.id))).first()
        role = UserRole.SUPERADMIN.value if total is None else UserRole.USER.value

        user = User(email=email, name=name.strip(), password_hash=hash_password(password), role=role)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def verify_credentials(self, *, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def send_verification_email(self, user: User) -> None:
        settings = get_settings()
        raw = token_urlsafe()
        t = EmailVerificationToken(
            user_id=user.id,
            token_hash=token_hash(raw),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        self._session.add(t)
        await self._session.flush()
        url = f"{settings.app_base_url}/verify?token={raw}"
        send_email(to=user.email, subject="验证你的邮箱", content=f"请点击链接完成验证：\n{url}\n")

    async def verify_email(self, raw_token: str) -> bool:
        h = token_hash(raw_token)
        result = await self._session.execute(
            select(EmailVerificationToken).where(EmailVerificationToken.token_hash == h)
        )
        t = result.scalar_one_or_none()
        if not t:
            return False
        now = datetime.now(timezone.utc)
        if t.used_at is not None or self._is_expired(t.expires_at):
            return False
        result_user = await self._session.execute(select(User).where(User.id == t.user_id))
        user = result_user.scalar_one_or_none()
        if not user:
            return False
        user.is_email_verified = True
        t.used_at = now
        await self._session.flush()
        return True

    async def send_password_reset_email(self, email: str) -> None:
        user = await self.get_user_by_email(email)
        if not user:
            return
        settings = get_settings()
        raw = token_urlsafe()
        t = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash(raw),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
        )
        self._session.add(t)
        await self._session.flush()
        url = f"{settings.app_base_url}/reset?token={raw}"
        send_email(to=user.email, subject="重置你的密码", content=f"请点击链接重置密码：\n{url}\n")

    async def create_session(self, *, user: User, remember_me: bool, user_agent: Optional[str] = None) -> UserSession:
        now = datetime.now(timezone.utc)
        settings = get_settings()
        expires = now + (timedelta(days=settings.remember_me_days) if remember_me else timedelta(minutes=settings.access_token_expires_minutes))
        session = UserSession(
            user_id=str(user.id),
            token_hash=token_hash(token_urlsafe()),
            remember_me=remember_me,
            expires_at=expires,
            user_agent=user_agent,
        )
        self._session.add(session)
        await self._session.flush()
        await self._session.refresh(session)
        return session

    async def reset_password(self, *, raw_token: str, new_password: str) -> bool:
        if not _password_ok(new_password):
            raise ValueError("密码强度不足")
        h = token_hash(raw_token)
        result = await self._session.execute(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == h)
        )
        t = result.scalar_one_or_none()
        if not t:
            return False
        now = datetime.now(timezone.utc)
        if t.used_at is not None or self._is_expired(t.expires_at):
            return False
        result_user = await self._session.execute(select(User).where(User.id == t.user_id))
        user = result_user.scalar_one_or_none()
        if not user:
            return False
        user.password_hash = hash_password(new_password)
        t.used_at = now
        await self._session.flush()
        return True
