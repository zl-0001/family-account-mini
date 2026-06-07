from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Record, Category, Account
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
import calendar


class RecordService:
    def __init__(self, db: Session):
        self.db = db

    def _update_account_balance(self, account_id: int, record_type: str, amount: Decimal, is_delete: bool = False):
        """更新账户余额"""
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if account:
            multiplier = -1 if is_delete else 1
            if record_type == "income":
                account.balance += amount * multiplier
            elif record_type == "expense":
                account.balance -= amount * multiplier
            # investment 类型不影响余额
            self.db.commit()

    def create(self, record_data, user_id: int) -> Record:
        """创建记账记录"""
        # 转换日期字符串为 date 对象
        if isinstance(record_data.record_date, str):
            record_date_obj = datetime.strptime(record_data.record_date, "%Y-%m-%d").date()
        else:
            record_date_obj = record_data.record_date

        record = Record(
            user_id=user_id,
            account_id=record_data.account_id,
            category_id=record_data.category_id,
            type=record_data.type,
            amount=record_data.amount,
            record_date=record_date_obj,
            remark=record_data.remark,
            is_fixed=record_data.is_fixed,
            fixed_cycle=record_data.fixed_cycle,
            remaining_years=record_data.remaining_years,
            reimbursement_status=record_data.reimbursement_status or "none"
        )
        self.db.add(record)

        # 更新账户余额
        self._update_account_balance(record_data.account_id, record_data.type, record_data.amount)

        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record_id: int, data, user_id: int) -> Optional[Record]:
        """更新记账记录"""
        record = self.db.query(Record).filter(
            Record.id == record_id,
            Record.user_id == user_id
        ).first()
        if not record:
            return None

        # 如果金额或账户变化，需要调整旧余额
        old_amount = record.amount
        old_account_id = record.account_id
        old_type = record.type

        if data.amount is not None:
            record.amount = data.amount
        if hasattr(data, 'remark') and data.remark is not None:
            record.remark = data.remark
        if hasattr(data, 'is_fixed') and data.is_fixed is not None:
            record.is_fixed = data.is_fixed

        # 恢复旧账户余额
        if old_type != "investment":
            if old_type == "income":
                self.db.query(Account).filter(Account.id == old_account_id).first().balance -= old_amount
            elif old_type == "expense":
                self.db.query(Account).filter(Account.id == old_account_id).first().balance += old_amount

        # 更新新账户余额
        new_account_id = data.account_id if hasattr(data, 'account_id') and data.account_id else old_account_id
        new_type = data.type if hasattr(data, 'type') and data.type else old_type
        new_amount = data.amount if data.amount is not None else old_amount

        if new_type != "investment":
            if new_type == "income":
                self.db.query(Account).filter(Account.id == new_account_id).first().balance += new_amount
            elif new_type == "expense":
                self.db.query(Account).filter(Account.id == new_account_id).first().balance -= new_amount

        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record_id: int, user_id: int) -> bool:
        """删除记账记录"""
        record = self.db.query(Record).filter(
            Record.id == record_id,
            Record.user_id == user_id
        ).first()
        if not record:
            return False

        # 恢复账户余额
        self._update_account_balance(record.account_id, record.type, record.amount, is_delete=True)

        self.db.delete(record)
        self.db.commit()
        return True

    def get_list(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        record_type: Optional[str] = None,
        category_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Record]:
        """获取记账记录列表"""
        query = self.db.query(Record).filter(Record.user_id == user_id)
        
        if start_date:
            query = query.filter(Record.record_date >= start_date)
        if end_date:
            query = query.filter(Record.record_date <= end_date)
        if record_type:
            query = query.filter(Record.type == record_type)
        if category_id:
            query = query.filter(Record.category_id == category_id)
        
        return query.order_by(Record.record_date.desc()).offset(skip).limit(limit).all()

    def get_monthly_stats(self, user_id: int, year: int, month: int) -> dict:
        """获取月度统计"""
        # 计算月份范围
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
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "income_trend": round(income_trend, 2),
            "expense_trend": round(expense_trend, 2),
            "budget_percent": 0.0,
            "categories": []
        }

    def get_fixed_records(self, user_id: int) -> List[Record]:
        """获取固定收支记录"""
        return self.db.query(Record).filter(
            Record.user_id == user_id,
            Record.is_fixed == True
        ).order_by(Record.record_date).all()
