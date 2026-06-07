from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime


class InvestmentCreate(BaseModel):
    """创建投资记录"""
    account_id: int
    name: str = Field(..., max_length=100)
    type: str  # stock, fund, 理财, deposit, bond, other
    buy_date: str  # YYYY-MM-DD
    amount: Decimal = Field(..., gt=0)
    buy_price: Optional[Decimal] = None
    quantity: Optional[Decimal] = None
    code: Optional[str] = None
    remark: Optional[str] = None


class InvestmentUpdate(BaseModel):
    """更新投资记录"""
    name: Optional[str] = None
    buy_price: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    quantity: Optional[Decimal] = None
    remark: Optional[str] = None


class InvestmentValueCreate(BaseModel):
    """记录月度市值"""
    update_month: str  # YYYY-MM
    current_value: Decimal
    profit_loss: Optional[Decimal] = 0
    dividend: Optional[Decimal] = 0
    remark: Optional[str] = None


class InvestmentResponse(BaseModel):
    """投资响应"""
    id: int
    user_id: int
    account_id: int
    name: str
    type: str
    code: Optional[str]
    buy_price: Optional[Decimal]
    current_price: Optional[Decimal]
    quantity: Optional[Decimal]
    amount: Decimal
    profit: Decimal
    buy_date: str
    sell_date: Optional[str]
    status: str
    remark: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class InvestmentValueResponse(BaseModel):
    """市值记录响应"""
    id: int
    investment_id: int
    update_month: str
    current_value: Decimal
    profit_loss: Decimal
    dividend: Decimal
    remark: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """投资组合汇总"""
    total_invested: Decimal  # 总投入
    total_value: Decimal     # 总市值
    total_profit: Decimal    # 累计收益
    profit_rate: float       # 收益率
    positions: List[dict]     # 各持仓详情
    allocation: List[dict]    # 资产配置


class InvestmentStats(BaseModel):
    """投资收益统计"""
    total_invested: Decimal
    total_value: Decimal
    total_profit: Decimal
    profit_rate: float
    monthly_data: List[dict]  # 月度收益变化
