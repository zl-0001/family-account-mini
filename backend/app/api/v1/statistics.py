from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.statistics_service import StatisticsService
from pydantic import BaseModel


# 响应模型
class MonthlyStatistics(BaseModel):
    income: float
    expense: float
    balance: float
    income_trend: float
    expense_trend: float
    budget_percent: float
    categories: List[dict]


class YearlyStatistics(BaseModel):
    year: int
    total_income: float
    total_expense: float
    total_balance: float
    monthly_data: List[dict]


class CategoryStatistics(BaseModel):
    category_id: int
    category_name: str
    amount: float
    percent: float
    count: int


router = APIRouter(prefix="/statistics", tags=["统计分析"])


@router.get("/monthly", response_model=MonthlyStatistics)
def get_monthly_statistics(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取月度统计数据"""
    service = StatisticsService(db)
    return service.get_monthly_stats(current_user.id, year, month)


@router.get("/yearly", response_model=YearlyStatistics)
def get_yearly_statistics(
    year: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取年度统计数据"""
    service = StatisticsService(db)
    return service.get_yearly_stats(current_user.id, year)


@router.get("/category", response_model=List[CategoryStatistics])
def get_category_statistics(
    year: int,
    month: int,
    record_type: str = "expense",
    parent_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取分类统计数据"""
    service = StatisticsService(db)
    return service.get_category_stats(current_user.id, year, month, record_type, parent_id)


@router.get("/trend")
def get_trend(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取收支趋势"""
    service = StatisticsService(db)
    return service.get_trend(current_user.id, months)
