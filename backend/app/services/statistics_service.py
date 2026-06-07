from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Record, Category
from typing import List
from datetime import date
from decimal import Decimal
import calendar


class StatisticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_monthly_stats(self, user_id: int, year: int, month: int) -> dict:
        """获取月度统计"""
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)
        
        # 查询本月收入
        income = self.db.query(func.sum(Record.amount)).filter(
            Record.user_id == user_id,
            Record.type == "income",
            Record.record_date >= start_date,
            Record.record_date <= end_date
        ).scalar() or Decimal("0")
        
        # 查询本月支出
        expense = self.db.query(func.sum(Record.amount)).filter(
            Record.user_id == user_id,
            Record.type == "expense",
            Record.record_date >= start_date,
            Record.record_date <= end_date
        ).scalar() or Decimal("0")
        
        # 计算环比
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_start = date(prev_year, prev_month, 1)
        _, prev_last_day = calendar.monthrange(prev_year, prev_month)
        prev_end = date(prev_year, prev_month, prev_last_day)
        
        prev_income = self.db.query(func.sum(Record.amount)).filter(
            Record.user_id == user_id,
            Record.type == "income",
            Record.record_date >= prev_start,
            Record.record_date <= prev_end
        ).scalar() or Decimal("0")
        
        prev_expense = self.db.query(func.sum(Record.amount)).filter(
            Record.user_id == user_id,
            Record.type == "expense",
            Record.record_date >= prev_start,
            Record.record_date <= prev_end
        ).scalar() or Decimal("0")
        
        income_trend = float((income - prev_income) / prev_income * 100) if prev_income > 0 else 0.0
        expense_trend = float((expense - prev_expense) / prev_expense * 100) if prev_expense > 0 else 0.0
        
        return {
            "income": float(income),
            "expense": float(expense),
            "balance": float(income - expense),
            "income_trend": round(income_trend, 2),
            "expense_trend": round(expense_trend, 2),
            "budget_percent": 0.0,
            "categories": []
        }

    def get_yearly_stats(self, user_id: int, year: int) -> dict:
        """获取年度统计"""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        income = self.db.query(func.sum(Record.amount)).filter(
            Record.user_id == user_id,
            Record.type == "income",
            Record.record_date >= start_date,
            Record.record_date <= end_date
        ).scalar() or Decimal("0")
        
        expense = self.db.query(func.sum(Record.amount)).filter(
            Record.user_id == user_id,
            Record.type == "expense",
            Record.record_date >= start_date,
            Record.record_date <= end_date
        ).scalar() or Decimal("0")
        
        # 按月统计
        monthly_data = []
        for month in range(1, 13):
            month_start = date(year, month, 1)
            _, last_day = calendar.monthrange(year, month)
            month_end = date(year, month, last_day)
            
            month_income = self.db.query(func.sum(Record.amount)).filter(
                Record.user_id == user_id,
                Record.type == "income",
                Record.record_date >= month_start,
                Record.record_date <= month_end
            ).scalar() or Decimal("0")
            
            month_expense = self.db.query(func.sum(Record.amount)).filter(
                Record.user_id == user_id,
                Record.type == "expense",
                Record.record_date >= month_start,
                Record.record_date <= month_end
            ).scalar() or Decimal("0")
            
            monthly_data.append({
                "month": month,
                "income": float(month_income),
                "expense": float(month_expense),
                "balance": float(month_income - month_expense)
            })
        
        return {
            "year": year,
            "total_income": income,
            "total_expense": expense,
            "total_balance": income - expense,
            "monthly_data": monthly_data
        }

    def get_category_stats(self, user_id: int, year: int, month: int, record_type: str, parent_id: int = None) -> List[dict]:
        """获取分类统计"""
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)

        query = self.db.query(
            Record.category_id,
            func.sum(Record.amount).label("total_amount"),
            func.count(Record.id).label("count")
        ).filter(
            Record.user_id == user_id,
            Record.type == record_type,
            Record.record_date >= start_date,
            Record.record_date <= end_date
        )

        if parent_id is not None:
            child_ids = [c.id for c in self.db.query(Category).filter(Category.parent_id == parent_id).all()]
            if child_ids:
                query = query.filter(Record.category_id.in_(child_ids))
            else:
                query = query.filter(Record.category_id == parent_id)

        results = query.group_by(Record.category_id).all()
        
        # 计算总金额
        total = sum(r.total_amount for r in results)
        
        # 组装结果
        stats = []
        for r in results:
            category = self.db.query(Category).filter(Category.id == r.category_id).first()
            stats.append({
                "category_id": r.category_id,
                "category_name": category.name if category else "未知",
                "amount": float(r.total_amount),
                "percent": float(r.total_amount / total * 100) if total > 0 else 0.0,
                "count": r.count
            })
        
        return sorted(stats, key=lambda x: x["amount"], reverse=True)

    def get_trend(self, user_id: int, months: int = 6) -> List[dict]:
        """获取收支趋势"""
        from datetime import datetime
        trend = []
        now = datetime.now()
        
        for i in range(months - 1, -1, -1):
            month_date = date(now.year, now.month, 1)
            if i > 0:
                # 往前推 i 个月
                month = now.month - i
                year = now.year
                while month <= 0:
                    month += 12
                    year -= 1
                month_date = date(year, month, 1)
            
            year = month_date.year
            month = month_date.month
            
            _, last_day = calendar.monthrange(year, month)
            end_date = date(year, month, last_day)
            
            income = self.db.query(func.sum(Record.amount)).filter(
                Record.user_id == user_id,
                Record.type == "income",
                Record.record_date >= month_date,
                Record.record_date <= end_date
            ).scalar() or Decimal("0")
            
            expense = self.db.query(func.sum(Record.amount)).filter(
                Record.user_id == user_id,
                Record.type == "expense",
                Record.record_date >= month_date,
                Record.record_date <= end_date
            ).scalar() or Decimal("0")
            
            trend.append({
                "month": f"{year}-{month:02d}",
                "income": float(income),
                "expense": float(expense),
                "balance": float(income - expense)
            })
        
        return trend
