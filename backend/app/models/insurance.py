from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func
from app.core.database import Base


class Insurance(Base):
    """保险表"""
    __tablename__ = "insurances"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    family_id = Column(Integer, nullable=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False, index=True)
    sub_type = Column(String(50))
    company = Column(String(100))
    policy_no = Column(String(50))
    insured_amount = Column(Numeric(12, 2))
    premium = Column(Numeric(12, 2), nullable=False)
    payment_cycle = Column(String(20), default="yearly")
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=False)
    beneficiary = Column(String(50))
    reminder_days = Column(Integer, default=3)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Insurance(id={self.id}, name='{self.name}', premium={self.premium})>"
