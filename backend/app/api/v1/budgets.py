from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.budget_service import BudgetService
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetSummary

router = APIRouter(prefix="/budgets", tags=["预算管理"])


@router.post("", response_model=BudgetResponse)
def create_or_update_budget(
    data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建或更新月度预算"""
    service = BudgetService(db)
    return service.create_or_update(data, current_user.id)


@router.get("", response_model=List[BudgetResponse])
def get_budgets(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取指定月份的预算列表"""
    service = BudgetService(db)
    return service.get_list(current_user.id, year, month)


@router.get("/summary", response_model=BudgetSummary)
def get_budget_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取预算执行情况"""
    service = BudgetService(db)
    return service.get_summary(current_user.id, year, month)


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新预算"""
    service = BudgetService(db)
    result = service.update(budget_id, data, current_user.id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="预算不存在")
    return result


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除预算"""
    service = BudgetService(db)
    success = service.delete(budget_id, current_user.id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="预算不存在")
    return {"message": "删除成功"}
