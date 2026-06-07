from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Budget, Record, Category
from typing import List, Optional
from datetime import date
from decimal import Decimal
import calendar


class BudgetService:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update(self, data, user_id: int) -> Budget:
        """创建或更新月度预算"""
        # 检查是否已存在同类型预算
        existing = self.db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.category_id == data.category_id,
            Budget.month == data.month,
            Budget.year == data.year
        ).first()

        if existing:
            # 更新
            existing.amount = data.amount
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # 创建
            budget = Budget(
                user_id=user_id,
                category_id=data.category_id,
                amount=data.amount,
                month=data.month,
                year=data.year
            )
            self.db.add(budget)
            self.db.commit()
            self.db.refresh(budget)
            return budget

    def get_list(self, user_id: int, year: int, month: int) -> List[Budget]:
        """获取指定月份的预算列表"""
        return self.db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.year == year,
            Budget.month == month
        ).all()

    def get_budget(self, user_id: int, budget_id: int) -> Optional[Budget]:
        """获取预算详情"""
        return self.db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()

    def update(self, budget_id: int, data, user_id: int) -> Optional[Budget]:
        """更新预算"""
        budget = self.get_budget(user_id, budget_id)
        if not budget:
            return None
        if data.amount is not None:
            budget.amount = data.amount
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def delete(self, budget_id: int, user_id: int) -> bool:
        """删除预算"""
        budget = self.get_budget(user_id, budget_id)
        if not budget:
            return False
        self.db.delete(budget)
        self.db.commit()
        return True

    def get_summary(self, user_id: int, year: int, month: int) -> dict:
        """获取预算执行情况"""
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)

        # 获取所有预算
        budgets = self.get_list(user_id, year, month)

        # 计算总预算
        total_budget = sum(b.amount for b in budgets if b.category_id is None)
        category_budgets = {b.category_id: b for b in budgets if b.category_id is not None}

        # 计算实际支出
        total_spent = self.db.query(func.sum(Record.amount)).filter(
            Record.user_id == user_id,
            Record.type == "expense",
            Record.record_date >= start_date,
            Record.record_date <= end_date
        ).scalar() or Decimal("0")

        # 计算各类别支出
        category_spent = {}
        if category_budgets:
            results = self.db.query(
                Record.category_id,
                func.sum(Record.amount).label("total")
            ).filter(
                Record.user_id == user_id,
                Record.type == "expense",
                Record.record_date >= start_date,
                Record.record_date <= end_date,
                Record.category_id.in_(category_budgets.keys())
            ).group_by(Record.category_id).all()

            for r in results:
                category_spent[r.category_id] = r.total

        # 组装类别详情
        categories = []
        for cat_id, budget in category_budgets.items():
            spent = category_spent.get(cat_id, Decimal("0"))
            category = self.db.query(Category).filter(Category.id == cat_id).first()
            categories.append({
                "category_id": cat_id,
                "category_name": category.name if category else "未知",
                "budget": float(budget.amount),
                "spent": float(spent),
                "remaining": float(budget.amount - spent),
                "percent": float(spent / budget.amount * 100) if budget.amount > 0 else 0
            })

        return {
            "month": month,
            "year": year,
            "total_budget": float(total_budget),
            "total_spent": float(total_spent),
            "total_remaining": float(total_budget - total_spent),
            "percent": float(total_spent / total_budget * 100) if total_budget > 0 else 0,
            "categories": categories
        }
