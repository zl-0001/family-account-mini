from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime


class BudgetCreate(BaseModel):
    """创建预算请求"""
    category_id: Optional[int] = None  # null 表示总预算
    amount: Decimal = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int


class BudgetUpdate(BaseModel):
    """更新预算请求"""
    amount: Optional[Decimal] = None


class BudgetResponse(BaseModel):
    """预算响应"""
    id: int
    user_id: int
    category_id: Optional[int]
    amount: Decimal
    month: int
    year: int
    spent: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class BudgetSummary(BaseModel):
    """预算汇总"""
    month: int
    year: int
    total_budget: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    percent: float
    categories: List[dict]
