from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.record_service import RecordService
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import datetime


# 请求/响应模型
class RecordCreate(BaseModel):
    account_id: int
    category_id: int
    type: str  # income, expense, investment
    amount: Decimal = Field(..., gt=0)
    record_date: str  # YYYY-MM-DD
    remark: Optional[str] = None
    is_fixed: bool = False
    fixed_cycle: Optional[str] = None
    remaining_years: Optional[Decimal] = None
    reimbursement_status: Optional[str] = "none"


class RecordUpdate(BaseModel):
    """更新记账记录请求"""
    amount: Optional[Decimal] = None
    remark: Optional[str] = None
    is_fixed: Optional[bool] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    type: Optional[str] = None
    record_date: Optional[str] = None


class RecordResponse(BaseModel):
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
    reimbursement_status: str
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator('record_date', mode='before')
    @classmethod
    def parse_record_date(cls, v):
        from datetime import date, datetime
        if isinstance(v, (date, datetime)):
            return v.isoformat()
        return v


class MonthlyStatistics(BaseModel):
    income: Decimal
    expense: Decimal
    balance: Decimal
    income_trend: float
    expense_trend: float
    budget_percent: float
    categories: List[dict]


router = APIRouter(prefix="/records", tags=["记账"])


@router.post("", response_model=RecordResponse)
def create_record(
    record_data: RecordCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建记账记录"""
    service = RecordService(db)
    return service.create(record_data, current_user.id)


@router.get("", response_model=List[RecordResponse])
def get_records(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    record_type: Optional[str] = None,
    category_id: Optional[int] = None,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取记账记录列表（默认合并家庭；user_id 指定按某成员筛）"""
    service = RecordService(db)
    return service.get_list(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        record_type=record_type,
        category_id=category_id,
        skip=skip,
        limit=limit,
        filter_user_id=user_id
    )


@router.get("/statistics/monthly", response_model=MonthlyStatistics)
def get_monthly_statistics(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取月度统计数据"""
    service = RecordService(db)
    return service.get_monthly_stats(current_user.id, year, month)


@router.get("/fixed", response_model=List[RecordResponse])
def get_fixed_records(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取固定收支记录"""
    service = RecordService(db)
    return service.get_fixed_records(current_user.id)


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单条记录（仅本人）"""
    service = RecordService(db)
    result = service.get_by_id(record_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="记录不存在")
    return result


@router.put("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    data: RecordUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新记账记录"""
    service = RecordService(db)
    result = service.update(record_id, data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="记录不存在")
    return result


@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除记账记录"""
    service = RecordService(db)
    success = service.delete(record_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}
