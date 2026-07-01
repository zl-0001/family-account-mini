from sqlalchemy.orm import Session
from app.models import Category
from typing import List, Optional
from fastapi import HTTPException, status


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_list(self, user_id: int, category_type: Optional[str] = None) -> List[Category]:
        """获取分类列表（包含系统预设和用户自定义）"""
        query = self.db.query(Category).filter(
            (Category.user_id == None) | (Category.user_id == user_id)
        )
        if category_type:
            query = query.filter(Category.type == category_type)
        return query.order_by(Category.sort_order, Category.id).all()

    def get_by_id(self, category_id: int) -> Category:
        """获取分类详情"""
        return self.db.query(Category).filter(Category.id == category_id).first()

    def create(self, data, user_id: int) -> Category:
        """创建自定义分类"""
        category = Category(
            user_id=user_id,
            name=data.name,
            type=data.type,
            parent_id=data.parent_id,
            icon=data.icon,
            color=data.color,
            is_fixed=data.is_fixed,
            group=data.group
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category_id: int, user_id: int) -> dict:
        """删除自定义分类"""
        category = self.db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在或无权删除"
            )

        self.db.delete(category)
        self.db.commit()
        return {"message": "删除成功"}

    def update(self, category_id: int, data, user_id: int) -> Optional[Category]:
        """更新分类"""
        category = self.db.query(Category).filter(
            Category.id == category_id,
            (Category.user_id == user_id) | (Category.user_id == None)
        ).first()

        if not category:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(category, field, value)

        self.db.commit()
        self.db.refresh(category)
        return category

    def reorder(self, items: list, user_id: int):
        """批量更新排序"""
        for item in items:
            category = self.db.query(Category).filter(
                Category.id == item.id,
                (Category.user_id == user_id) | (Category.user_id == None)
            ).first()
            if category:
                category.sort_order = item.sort_order
        self.db.commit()
