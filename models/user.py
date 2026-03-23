"""User ORM model."""

from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from common.const import USER_NAME_MAX_LENGTH
from models.base import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(USER_NAME_MAX_LENGTH), nullable=False, index=True)
    gender: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hobbies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
