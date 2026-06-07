from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FamilyCreate(BaseModel):
    """创建家庭请求"""
    name: str = Field(..., max_length=100)


class FamilyResponse(BaseModel):
    """家庭响应"""
    id: int
    name: str
    owner_id: int
    invite_code: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class FamilyMember(BaseModel):
    """家庭成员"""
    user_id: int
    username: str
    nickname: Optional[str]
    avatar: Optional[str]
    role: str  # owner, admin, member
    joined_at: datetime


class FamilyDetail(FamilyResponse):
    """家庭详情"""
    members: List[FamilyMember] = []


class JoinFamily(BaseModel):
    """加入家庭请求"""
    invite_code: str = Field(..., min_length=6, max_length=20)


class UpdateMemberRole(BaseModel):
    """更新成员角色"""
    role: str  # admin, member
