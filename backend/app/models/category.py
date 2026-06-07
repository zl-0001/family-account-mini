from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Category(Base):
    """分类表"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False, index=True)
    parent_id = Column(Integer, nullable=True)
    icon = Column(String(50))
    color = Column(String(20))
    sort_order = Column(Integer, default=0)
    is_fixed = Column(Boolean, default=False)
    group = Column(String(50), nullable=True)  # 所属分组
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type={self.type})>"
