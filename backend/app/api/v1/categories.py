from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.category_service import CategoryService
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# 请求/响应模型
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=50)
    type: str  # income, expense, investment
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_fixed: bool = False
    group: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    type: str
    parent_id: Optional[int]
    icon: Optional[str]
    color: Optional[str]
    is_fixed: bool
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


router = APIRouter(prefix="/categories", tags=["分类管理"])


@router.get("", response_model=List[CategoryResponse])
def get_categories(
    category_type: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取分类列表"""
    service = CategoryService(db)
    return service.get_list(current_user.id, category_type)


@router.post("", response_model=CategoryResponse)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建自定义分类"""
    service = CategoryService(db)
    return service.create(data, current_user.id)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取分类详情"""
    service = CategoryService(db)
    return service.get_by_id(category_id)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除自定义分类"""
    service = CategoryService(db)
    return service.delete(category_id, current_user.id)


class CategoryUpdate(BaseModel):
    """更新分类请求"""
    name: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_fixed: Optional[bool] = None
    group: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryReorderItem(BaseModel):
    id: int
    sort_order: int


@router.put("/reorder")
def reorder_categories(
    items: List[CategoryReorderItem],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """批量更新分类排序"""
    service = CategoryService(db)
    service.reorder(items, current_user.id)
    return {"message": "排序成功"}


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新分类"""
    service = CategoryService(db)
    result = service.update(category_id, data, current_user.id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="分类不存在或无权修改")
    return result
