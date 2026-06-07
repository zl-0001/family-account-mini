from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryCreate(BaseModel):
    """创建分类请求"""
    name: str = Field(..., max_length=50)
    type: str  # income, expense, investment
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_fixed: bool = False
    group: Optional[str] = None


class CategoryResponse(BaseModel):
    """分类响应"""
    id: int
    name: str
    type: str
    parent_id: Optional[int]
    icon: Optional[str]
    color: Optional[str]
    is_fixed: bool
    sort_order: int
    group: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
