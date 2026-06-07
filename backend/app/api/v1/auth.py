from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import create_access_token
from app.services.auth_service import AuthService
from app.services.wechat_service import WeChatService
from app.schemas.user import UserCreate, UserResponse, Token, UserUpdate

router = APIRouter(prefix="/auth", tags=["认证"])


class WeChatLoginRequest(BaseModel):
    code: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    service = AuthService(db)
    user = service.register(user_data)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    service = AuthService(db)
    user = service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/wechat-login", response_model=Token)
def wechat_login(request: WeChatLoginRequest, db: Session = Depends(get_db)):
    """微信登录"""
    # 用 code 换取 openid
    wechat_data = WeChatService.code2session(request.code)
    openid = wechat_data["openid"]

    # 查找或创建用户
    service = AuthService(db)
    user = service.wechat_login(openid, nickname=request.nickname, avatar=request.avatar)

    # 创建 JWT token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user = Depends(AuthService.get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    data: UserUpdate,
    current_user = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """更新当前用户资料"""
    if data.nickname is not None:
        current_user.nickname = data.nickname
    if data.avatar is not None:
        current_user.avatar = data.avatar
    if data.phone is not None:
        current_user.phone = data.phone
    db.commit()
    db.refresh(current_user)
    return current_user
