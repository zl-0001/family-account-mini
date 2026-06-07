from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from datetime import datetime


class AccountCreate(BaseModel):
    """创建账户请求"""
    name: str = Field(..., max_length=50)
    type: str  # cash, bank, alipay, wechat, credit_card, investment
    balance: Decimal = Decimal("0")
    icon: Optional[str] = None
    color: Optional[str] = None
    is_default: bool = False


class AccountUpdate(BaseModel):
    """更新账户请求"""
    name: Optional[str] = None
    balance: Optional[Decimal] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_default: Optional[bool] = None


class AccountResponse(BaseModel):
    """账户响应"""
    id: int
    user_id: int
    name: str
    type: str
    balance: Decimal
    icon: Optional[str]
    color: Optional[str]
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True
