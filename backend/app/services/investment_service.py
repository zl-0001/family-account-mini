from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Investment, InvestmentValue
from typing import List, Optional
from decimal import Decimal


class InvestmentService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data, user_id: int) -> Investment:
        """创建投资记录"""
        investment = Investment(
            user_id=user_id,
            account_id=data.account_id,
            name=data.name,
            type=data.type,
            code=data.code,
            buy_price=data.buy_price,
            quantity=data.quantity,
            amount=data.amount,
            buy_date=data.buy_date,
            remark=data.remark,
            status="holding"
        )
        self.db.add(investment)
        self.db.commit()
        self.db.refresh(investment)
        return investment

    def get_list(self, user_id: int, status: Optional[str] = None) -> List[Investment]:
        """获取投资列表"""
        query = self.db.query(Investment).filter(Investment.user_id == user_id)
        if status:
            query = query.filter(Investment.status == status)
        return query.order_by(Investment.created_at.desc()).all()

    def get_by_id(self, investment_id: int, user_id: int) -> Optional[Investment]:
        """获取投资详情"""
        return self.db.query(Investment).filter(
            Investment.id == investment_id,
            Investment.user_id == user_id
        ).first()

    def update(self, investment_id: int, data, user_id: int) -> Optional[Investment]:
        """更新投资信息"""
        investment = self.get_by_id(investment_id, user_id)
        if not investment:
            return None

        if data.name is not None:
            investment.name = data.name
        if data.buy_price is not None:
            investment.buy_price = data.buy_price
        if data.current_price is not None:
            investment.current_price = data.current_price
        if data.quantity is not None:
            investment.quantity = data.quantity
        if data.remark is not None:
            investment.remark = data.remark

        # 计算收益
        if investment.current_price and investment.buy_price and investment.quantity:
            investment.profit = (investment.current_price - investment.buy_price) * investment.quantity

        self.db.commit()
        self.db.refresh(investment)
        return investment

    def sell(self, investment_id: int, sell_date: str, user_id: int) -> Optional[Investment]:
        """卖出投资"""
        investment = self.get_by_id(investment_id, user_id)
        if not investment:
            return None

        investment.status = "sold"
        investment.sell_date = sell_date
        self.db.commit()
        self.db.refresh(investment)
        return investment

    def delete(self, investment_id: int, user_id: int) -> bool:
        """删除投资记录"""
        investment = self.get_by_id(investment_id, user_id)
        if not investment:
            return False

        # 删除关联的市值记录
        self.db.query(InvestmentValue).filter(
            InvestmentValue.investment_id == investment_id
        ).delete()

        self.db.delete(investment)
        self.db.commit()
        return True

    def add_value_record(self, investment_id: int, data, user_id: int) -> InvestmentValue:
        """记录月度市值"""
        investment = self.get_by_id(investment_id, user_id)
        if not investment:
            raise ValueError("投资不存在")

        # 检查是否已存在当月记录
        existing = self.db.query(InvestmentValue).filter(
            InvestmentValue.investment_id == investment_id,
            InvestmentValue.update_month == data.update_month
        ).first()

        if existing:
            existing.current_value = data.current_value
            existing.profit_loss = data.profit_loss or 0
            existing.dividend = data.dividend or 0
            existing.remark = data.remark
            self.db.commit()
            self.db.refresh(existing)
            return existing

        record = InvestmentValue(
            investment_id=investment_id,
            update_month=data.update_month,
            current_value=data.current_value,
            profit_loss=data.profit_loss or 0,
            dividend=data.dividend or 0,
            remark=data.remark
        )
        self.db.add(record)

        # 更新投资的当前价格和收益
        if investment.buy_price and data.current_value and investment.quantity:
            investment.current_price = data.current_value / investment.quantity
            investment.profit = data.current_value - (investment.buy_price * investment.quantity)

        self.db.commit()
        self.db.refresh(record)
        return record

    def get_value_history(self, investment_id: int, user_id: int) -> List[InvestmentValue]:
        """获取市值历史"""
        investment = self.get_by_id(investment_id, user_id)
        if not investment:
            raise ValueError("投资不存在")

        return self.db.query(InvestmentValue).filter(
            InvestmentValue.investment_id == investment_id
        ).order_by(InvestmentValue.update_month.desc()).all()

    def get_portfolio_summary(self, user_id: int) -> dict:
        """获取投资组合汇总"""
        investments = self.get_list(user_id, status="holding")

        total_invested = sum(i.amount for i in investments)
        total_value = sum(
            float(i.current_price * i.quantity) if i.current_price and i.quantity else float(i.amount)
            for i in investments
        )
        total_profit = total_value - float(total_invested)
        profit_rate = float(total_profit / total_invested * 100) if total_invested > 0 else 0

        # 各持仓详情
        positions = []
        for i in investments:
            current_val = float(i.current_price * i.quantity) if i.current_price and i.quantity else float(i.amount)
            profit = current_val - float(i.amount)
            positions.append({
                "id": i.id,
                "name": i.name,
                "type": i.type,
                "invested": float(i.amount),
                "value": current_val,
                "profit": profit,
                "profit_rate": float(profit / float(i.amount) * 100) if i.amount > 0 else 0,
                "buy_date": i.buy_date
            })

        # 资产配置
        allocation = []
        type_groups = {}
        for i in investments:
            current_val = float(i.current_price * i.quantity) if i.current_price and i.quantity else float(i.amount)
            if i.type not in type_groups:
                type_groups[i.type] = 0
            type_groups[i.type] += current_val

        total = sum(type_groups.values())
        for t, v in type_groups.items():
            allocation.append({
                "type": t,
                "value": v,
                "percent": float(v / total * 100) if total > 0 else 0
            })

        return {
            "total_invested": total_invested,
            "total_value": Decimal(str(total_value)),
            "total_profit": Decimal(str(total_profit)),
            "profit_rate": round(profit_rate, 2),
            "positions": positions,
            "allocation": allocation
        }

    def get_stats(self, user_id: int) -> dict:
        """获取投资收益统计"""
        all_investments = self.db.query(Investment).filter(Investment.user_id == user_id).all()

        total_invested = sum(i.amount for i in all_investments if i.status == "holding")
        total_value = sum(
            float(i.current_price * i.quantity) if i.current_price and i.quantity else float(i.amount)
            for i in all_investments if i.status == "holding"
        )
        total_profit = total_value - float(total_invested)
        profit_rate = float(total_profit / float(total_invested) * 100) if total_invested > 0 else 0

        return {
            "total_invested": total_invested,
            "total_value": Decimal(str(total_value)),
            "total_profit": Decimal(str(total_profit)),
            "profit_rate": round(profit_rate, 2),
            "monthly_data": []
        }
