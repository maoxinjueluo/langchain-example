"""Async SQLAlchemy engine and session for SQLite."""

from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from common.const import DB_DIR_NAME, DB_FILE_NAME, DB_ECHO

PROJECT_ROOT = Path(__file__).resolve().parent
DB_DIR = PROJECT_ROOT / DB_DIR_NAME
DB_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite+aiosqlite:///{DB_DIR / DB_FILE_NAME}"

engine = create_async_engine(
    DATABASE_URL,
    echo=DB_ECHO,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    from models.base import Base
    from models.user import UserModel  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
