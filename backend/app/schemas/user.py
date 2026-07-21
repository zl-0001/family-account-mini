from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    nickname: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    nickname: Optional[str]
    avatar: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    role: str
    family_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class UserUpdate(BaseModel):
    """更新用户资料"""
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
