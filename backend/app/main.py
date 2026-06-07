"""
家庭记账应用 - 后端入口文件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import auth, records, categories, accounts, statistics, budgets, families, investments

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="家庭记账应用后端API",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS配置 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(records.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(statistics.router, prefix="/api/v1")
app.include_router(budgets.router, prefix="/api/v1")
app.include_router(families.router, prefix="/api/v1")
app.include_router(investments.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()


@app.get("/", tags=["Root"])
def root():
    """根路径"""
    return {
        "message": "家庭记账API服务",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


@app.get("/health", tags=["Root"])
def health_check():
    """健康检查"""
    return {"status": "healthy"}
