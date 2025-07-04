"""
FastAPI应用主文件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
import logging

from .routers import analysis, models, health
from .middleware import LoggingMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    app = FastAPI(
        title="时间序列模型传递函数分析器 API",
        description="基于ARIMA/SARIMA模型的传递函数自动推导服务",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境中应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加日志中间件
    app.add_middleware(LoggingMiddleware)
    
    # 注册路由
    app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
    app.include_router(models.router, prefix="/api/v1", tags=["模型管理"])
    app.include_router(analysis.router, prefix="/api/v1", tags=["分析服务"])
    
    # 全局异常处理
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status_code": exc.status_code}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        logger.error(f"请求验证错误: {exc}")
        return JSONResponse(
            status_code=422,
            content={"error": "请求参数验证失败", "details": exc.errors()}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"未处理的异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "服务器内部错误", "message": str(exc)}
        )
    
    logger.info("FastAPI应用创建成功")
    return app
