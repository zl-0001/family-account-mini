from sqlalchemy.orm import Session
from app.models import Account
from typing import List
from fastapi import HTTPException, status


class AccountService:
    def __init__(self, db: Session):
        self.db = db

    def get_list(self, user_id: int) -> List[Account]:
        """获取账户列表"""
        return self.db.query(Account).filter(
            Account.user_id == user_id
        ).order_by(Account.is_default.desc(), Account.id).all()

    def get_by_id(self, account_id: int, user_id: int) -> Account:
        """获取账户详情"""
        return self.db.query(Account).filter(
            Account.id == account_id,
            Account.user_id == user_id
        ).first()

    def create(self, data, user_id: int) -> Account:
        """创建账户"""
        # 如果设为默认，先取消其他默认账户
        if data.is_default:
            self.db.query(Account).filter(
                Account.user_id == user_id,
                Account.is_default == True
            ).update({"is_default": False})
        
        account = Account(
            user_id=user_id,
            name=data.name,
            type=data.type,
            balance=data.balance,
            icon=data.icon,
            color=data.color,
            is_default=data.is_default
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update(self, account_id: int, data, user_id: int) -> Account:
        """更新账户"""
        account = self.get_by_id(account_id, user_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="账户不存在"
            )
        
        # 如果设为默认，先取消其他默认账户
        if data.is_default:
            self.db.query(Account).filter(
                Account.user_id == user_id,
                Account.is_default == True,
                Account.id != account_id
            ).update({"is_default": False})
        
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(account, key, value)
        
        self.db.commit()
        self.db.refresh(account)
        return account

    def delete(self, account_id: int, user_id: int) -> dict:
        """删除账户"""
        account = self.get_by_id(account_id, user_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="账户不存在"
            )
        
        self.db.delete(account)
        self.db.commit()
        return {"message": "删除成功"}
