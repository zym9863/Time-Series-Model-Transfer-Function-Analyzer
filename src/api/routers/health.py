"""
健康检查路由
"""

from datetime import datetime
from fastapi import APIRouter
from ..schemas import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check():
    """
    检查服务健康状态
    
    Returns:
        HealthResponse: 服务状态信息
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat()
    )
