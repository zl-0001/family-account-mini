import enum
from sqlalchemy import Column, BigInteger, String, DateTime, Enum, ForeignKey, Numeric, Date, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserRole(str, enum.Enum):
    """用户角色"""
    owner = "owner"      # 家庭创建者
    admin = "admin"      # 管理员
    member = "member"    # 普通成员


class RecordType(str, enum.Enum):
    """记录类型"""
    income = "income"        # 收入
    expense = "expense"      # 支出
    investment = "investment" # 投资


class FixedCycle(str, enum.Enum):
    """固定周期"""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class ReimbursementStatus(str, enum.Enum):
    """报销状态"""
    none = "none"        # 无需报销
    pending = "pending"  # 待报销
    done = "done"        # 已报销


class AccountType(str, enum.Enum):
    """账户类型"""
    cash = "cash"              # 现金
    bank = "bank"              # 银行卡
    alipay = "alipay"          # 支付宝
    wechat = "wechat"          # 微信
    credit_card = "credit_card" # 信用卡
    investment = "investment"   # 投资账户


class InvestmentType(str, enum.Enum):
    """投资类型"""
    stock = "stock"    # 股票
    fund = "fund"      # 基金
    bond = "bond"      # 债券
    deposit = "deposit" # 定期存款
    other = "other"    # 其他


class InsuranceType(str, enum.Enum):
    """保险类型"""
    life = "life"           # 寿险
    health = "health"       # 健康险
    accident = "accident"   # 意外险
    car = "car"             # 车险
    property = "property"   # 财产险
    other = "other"         # 其他
