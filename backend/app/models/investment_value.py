from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class InvestmentValue(Base):
    """投资市值记录表"""
    __tablename__ = "investment_values"

    id = Column(Integer, primary_key=True)
    investment_id = Column(Integer, ForeignKey("investments.id"), nullable=False, index=True)
    update_month = Column(String(7), nullable=False)  # YYYY-MM
    current_value = Column(Numeric(12, 2), nullable=False)
    profit_loss = Column(Numeric(12, 2), default=0)
    dividend = Column(Numeric(12, 2), default=0)
    remark = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<InvestmentValue(investment_id={self.investment_id}, month={self.update_month}, value={self.current_value})>"
