from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func
from app.core.database import Base


class Investment(Base):
    """投资记录表"""
    __tablename__ = "investments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    account_id = Column(Integer, nullable=False)
    type = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20))
    buy_price = Column(Numeric(12, 4))
    current_price = Column(Numeric(12, 4))
    quantity = Column(Numeric(12, 4))
    amount = Column(Numeric(12, 2), nullable=False)
    profit = Column(Numeric(12, 2), default=0)
    buy_date = Column(String(10), nullable=False)
    sell_date = Column(String(10), nullable=True)
    status = Column(String(20), default="holding")
    remark = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Investment(id={self.id}, name='{self.name}', amount={self.amount})>"
