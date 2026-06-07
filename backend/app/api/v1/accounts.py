from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.account_service import AccountService
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from datetime import datetime


# 请求/响应模型
class AccountCreate(BaseModel):
    name: str = Field(..., max_length=50)
    type: str  # cash, bank, alipay, wechat, credit_card, investment
    balance: Decimal = Decimal("0")
    icon: Optional[str] = None
    color: Optional[str] = None
    is_default: bool = False


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    balance: Optional[Decimal] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_default: Optional[bool] = None


class AccountResponse(BaseModel):
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


router = APIRouter(prefix="/accounts", tags=["账户管理"])


@router.get("", response_model=List[AccountResponse])
def get_accounts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取账户列表"""
    service = AccountService(db)
    return service.get_list(current_user.id)


@router.post("", response_model=AccountResponse)
def create_account(
    data: AccountCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建账户"""
    service = AccountService(db)
    return service.create(data, current_user.id)


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新账户"""
    service = AccountService(db)
    return service.update(account_id, data, current_user.id)


@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除账户"""
    service = AccountService(db)
    return service.delete(account_id, current_user.id)
