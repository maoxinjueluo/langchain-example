from typing import Optional

from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from common.const import KBVisibility, KBDocumentStatus
from models.base import BaseModel


class KnowledgeBase(BaseModel):
    __tablename__ = "knowledge_bases"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    visibility: Mapped[str] = mapped_column(String(32), default=KBVisibility.PRIVATE.value, nullable=False)
    owner_user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    permission_level: Mapped[str] = mapped_column(String(32), default="admin", nullable=False)


class KBDocument(BaseModel):
    __tablename__ = "kb_documents"

    knowledge_base_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    md5: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_status: Mapped[str] = mapped_column(String(32), default=KBDocumentStatus.UPLOADED.value, nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    file_ext: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (UniqueConstraint("knowledge_base_id", "md5", name="uq_kb_doc_md5"),)


class KBTag(BaseModel):
    __tablename__ = "kb_tags"

    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)


class KnowledgeBaseTag(BaseModel):
    __tablename__ = "knowledge_base_tags"

    knowledge_base_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    tag_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
