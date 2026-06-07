from sqlalchemy.orm import Session
from app.models import User
from app.core.security import get_password_hash, verify_password, get_current_user
from fastapi import Depends, HTTPException, status


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, user_data) -> User:
        """用户注册"""
        # 检查用户名是否已存在
        existing_user = self.db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )

        # 创建用户
        user = User(
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
            nickname=user_data.nickname or user_data.username,
            phone=getattr(user_data, 'phone', None),
            email=getattr(user_data, 'email', None)
        )
        self.db.add(user)
        self.db.flush()

        # 初始化预设分类
        from app.services.category_init_service import CategoryInitService
        CategoryInitService.init_categories_for_user(self.db, user.id)

        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> User:
        """验证用户"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def get_user_by_username(self, username: str) -> User:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> User:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_wechat_openid(self, openid: str) -> User:
        """根据微信openid获取用户"""
        return self.db.query(User).filter(User.wechat_openid == openid).first()

    def wechat_login(self, openid: str, nickname: str = None, avatar: str = None) -> User:
        """微信登录"""
        user = self.get_user_by_wechat_openid(openid)
        if user:
            return user

        user = User(
            username=f"wechat_{openid[:16]}",
            password_hash="",
            nickname=nickname or "微信用户",
            avatar=avatar,
            wechat_openid=openid,
        )
        self.db.add(user)
        self.db.flush()

        # 初始化预设分类
        from app.services.category_init_service import CategoryInitService
        CategoryInitService.init_categories_for_user(self.db, user.id)

        self.db.commit()
        self.db.refresh(user)
        return user

    @staticmethod
    def get_current_user(current_user = Depends(get_current_user)):
        """获取当前用户（依赖注入用）"""
        return current_user
