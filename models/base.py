"""Abstract ORM base with common columns."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from common.const import DEFAULT_STATUS


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    pass


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BaseModel(Base):
    """Shared columns: id, timestamps, status, json extension."""

    __abstract__ = True

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )
    status: Mapped[int] = mapped_column(Integer, default=DEFAULT_STATUS, nullable=False)
    json_extend: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
