"""
家庭记账应用 - 后端入口文件
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
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

logging.basicConfig(level=logging.INFO)


# 全局异常处理：记录日志；DEBUG 返回详情方便排查，生产环境只返回友好提示
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception(f"未捕获异常 {request.method} {request.url.path}: {exc}")
    if settings.DEBUG:
        import traceback
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "traceback": traceback.format_exc()},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"},
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
