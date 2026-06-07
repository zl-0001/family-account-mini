from sqlalchemy import Column, Integer, String, DateTime, Numeric, Date, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Record(Base):
    """记账记录表"""
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    family_id = Column(Integer, nullable=True)
    account_id = Column(Integer, nullable=False)
    category_id = Column(Integer, nullable=False)
    type = Column(String(20), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    record_date = Column(Date, nullable=False, index=True)
    remark = Column(String(255))
    is_fixed = Column(Boolean, default=False)
    fixed_cycle = Column(String(20), nullable=True)
    remaining_years = Column(Numeric(5, 2), nullable=True)  # 剩余年限（非必填）
    reimbursement_status = Column(String(20), default="none")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Record(id={self.id}, type={self.type}, amount={self.amount})>"
