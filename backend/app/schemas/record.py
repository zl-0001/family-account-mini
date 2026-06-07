from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from datetime import datetime


class RecordCreate(BaseModel):
    """创建记账记录请求"""
    account_id: int
    category_id: int
    type: str  # income, expense, investment
    amount: Decimal = Field(..., gt=0)
    record_date: str  # YYYY-MM-DD
    remark: Optional[str] = None
    is_fixed: bool = False
    fixed_cycle: Optional[str] = None
    remaining_years: Optional[Decimal] = None  # 剩余年限（非必填）
    reimbursement_status: Optional[str] = "none"


class RecordUpdate(BaseModel):
    """更新记账记录请求"""
    amount: Optional[Decimal] = None
    remark: Optional[str] = None
    is_fixed: Optional[bool] = None


class RecordResponse(BaseModel):
    """记账记录响应"""
    id: int
    user_id: int
    account_id: int
    category_id: int
    type: str
    amount: Decimal
    record_date: str
    remark: Optional[str]
    is_fixed: bool
    fixed_cycle: Optional[str]
    remaining_years: Optional[Decimal] = None
    reimbursement_status: str
    created_at: datetime

    class Config:
        from_attributes = True
