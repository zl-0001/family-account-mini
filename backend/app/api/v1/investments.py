from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.investment_service import InvestmentService
from app.schemas.investment import (
    InvestmentCreate, InvestmentUpdate, InvestmentResponse,
    InvestmentValueCreate, InvestmentValueResponse,
    PortfolioSummary, InvestmentStats
)

router = APIRouter(prefix="/investments", tags=["投资管理"])


@router.post("", response_model=InvestmentResponse)
def create_investment(
    data: InvestmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """添加投资记录"""
    service = InvestmentService(db)
    return service.create(data, current_user.id)


@router.get("", response_model=List[InvestmentResponse])
def get_investments(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取投资列表"""
    service = InvestmentService(db)
    return service.get_list(current_user.id, status)


@router.get("/portfolio", response_model=PortfolioSummary)
def get_portfolio(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取投资组合汇总"""
    service = InvestmentService(db)
    return service.get_portfolio_summary(current_user.id)


@router.get("/stats", response_model=InvestmentStats)
def get_investment_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取投资收益统计"""
    service = InvestmentService(db)
    return service.get_stats(current_user.id)


@router.get("/{investment_id}", response_model=InvestmentResponse)
def get_investment(
    investment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取投资详情"""
    service = InvestmentService(db)
    investment = service.get_by_id(investment_id, current_user.id)
    if not investment:
        raise HTTPException(status_code=404, detail="投资不存在")
    return investment


@router.put("/{investment_id}", response_model=InvestmentResponse)
def update_investment(
    investment_id: int,
    data: InvestmentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新投资信息"""
    service = InvestmentService(db)
    result = service.update(investment_id, data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="投资不存在")
    return result


@router.delete("/{investment_id}")
def delete_investment(
    investment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除投资记录"""
    service = InvestmentService(db)
    success = service.delete(investment_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="投资不存在")
    return {"message": "删除成功"}


@router.post("/{investment_id}/sell")
def sell_investment(
    investment_id: int,
    sell_date: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """卖出投资"""
    service = InvestmentService(db)
    result = service.sell(investment_id, sell_date, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="投资不存在")
    return {"message": "卖出成功"}


@router.post("/{investment_id}/values", response_model=InvestmentValueResponse)
def add_value_record(
    investment_id: int,
    data: InvestmentValueCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """记录月度市值"""
    service = InvestmentService(db)
    try:
        return service.add_value_record(investment_id, data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{investment_id}/values", response_model=List[InvestmentValueResponse])
def get_value_history(
    investment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取市值历史"""
    service = InvestmentService(db)
    try:
        return service.get_value_history(investment_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
