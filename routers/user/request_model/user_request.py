"""User API request bodies."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from common.const import (
    USER_NAME_MAX_LENGTH,
    USER_GENDER_MAX_LENGTH,
    USER_AGE_MIN,
    USER_AGE_MAX,
    DEFAULT_STATUS,
)


class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=USER_NAME_MAX_LENGTH, description="姓名")
    gender: Optional[int] = Field(None, description="性别")
    hobbies: Optional[str] = Field(None, description="爱好")
    age: Optional[int] = Field(None, ge=USER_AGE_MIN, le=USER_AGE_MAX, description="年龄")
    status: int = Field(DEFAULT_STATUS, description="状态")
    json_extend: Optional[Dict[str, Any]] = Field(None, description="JSON 扩展字段")


class UserBatchCreateRequest(BaseModel):
    items: List[UserCreateRequest] = Field(..., min_length=1, description="批量创建")


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=USER_NAME_MAX_LENGTH)
    gender: Optional[str] = Field(None, max_length=USER_GENDER_MAX_LENGTH)
    hobbies: Optional[str] = None
    age: Optional[int] = Field(None, ge=USER_AGE_MIN, le=USER_AGE_MAX)
    status: Optional[int] = None
    json_extend: Optional[Dict[str, Any]] = None


class UserBatchDeleteRequest(BaseModel):
    ids: List[int] = Field(..., min_length=1, description="要删除的用户 id 列表")


class UserBatchGetRequest(BaseModel):
    ids: List[int] = Field(..., min_length=1, description="查询的用户 id 列表")


class UserBatchUpdateItem(BaseModel):
    id: int = Field(..., description="用户 id")
    name: Optional[str] = Field(None, min_length=1, max_length=USER_NAME_MAX_LENGTH)
    gender: Optional[str] = Field(None, max_length=USER_GENDER_MAX_LENGTH)
    hobbies: Optional[str] = None
    age: Optional[int] = Field(None, ge=USER_AGE_MIN, le=USER_AGE_MAX)
    status: Optional[int] = None
    json_extend: Optional[Dict[str, Any]] = None


class UserBatchUpdateRequest(BaseModel):
    items: List[UserBatchUpdateItem] = Field(..., min_length=1, description="批量更新项")
