"""User API response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from common.const import MESSAGE_OK


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    gender: Optional[str]
    hobbies: Optional[str]
    age: Optional[int]
    status: int
    json_extend: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    total: int
    items: List[UserResponse]
    skip: int
    limit: int


class MessageResponse(BaseModel):
    message: str = Field(default=MESSAGE_OK)
    affected: Optional[int] = None
