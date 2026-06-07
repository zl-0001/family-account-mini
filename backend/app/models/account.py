from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Account(Base):
    """账户表"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)
    balance = Column(Numeric(12, 2), default=0)
    icon = Column(String(50))
    color = Column(String(20))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', balance={self.balance})>"
