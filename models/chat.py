from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Float, String, Text
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Conversation(BaseModel):
    __tablename__ = "conversations"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    knowledge_base_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)


class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB().with_variant(JSON, "sqlite"), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class AnswerFeedback(BaseModel):
    __tablename__ = "answer_feedback"

    message_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    is_helpful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class FavoriteQuestion(BaseModel):
    __tablename__ = "favorite_questions"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    message_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
