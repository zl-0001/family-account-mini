from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func
from app.core.database import Base


class Budget(Base):
    """预算表"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    family_id = Column(Integer, nullable=True)
    category_id = Column(Integer, nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    spent = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Budget(id={self.id}, year={self.year}, month={self.month}, amount={self.amount})>"
