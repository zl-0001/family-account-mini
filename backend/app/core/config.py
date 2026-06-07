from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List
import os


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "家庭记账API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return False

    # 数据库配置 - 支持SQLite和MySQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./family_account.db")

    # MySQL配置（可选）
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "family_account"

    # JWT配置 - 生产环境必须设置强密钥
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # CORS配置 - 生产环境必须指定具体域名
    BACKEND_CORS_ORIGINS: List[str] = []

    # 微信小程序配置
    WEIXIN_APPID: str = ""
    WEIXIN_APPSECRET: str = ""

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """获取CORS origins，支持环境变量和配置列表"""
        env_origins = os.getenv("CORS_ORIGINS", "")
        if env_origins:
            return [o.strip() for o in env_origins.split(",") if o.strip()]
        return self.BACKEND_CORS_ORIGINS

    class Config:
        env_file = ".env"


settings = Settings()

# 生产环境检查
if not settings.DEBUG and not settings.JWT_SECRET_KEY:
    import warnings
    warnings.warn("WARNING: JWT_SECRET_KEY not set in production!")
