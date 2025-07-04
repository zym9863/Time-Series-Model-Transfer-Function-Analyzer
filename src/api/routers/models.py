"""
模型管理路由
"""

from fastapi import APIRouter, HTTPException
from ..schemas import ModelListResponse

router = APIRouter()

@router.get("/models", response_model=ModelListResponse, summary="获取支持的模型类型")
async def get_supported_models():
    """
    获取系统支持的模型类型和示例
    
    Returns:
        ModelListResponse: 支持的模型类型列表和示例
    """
    return ModelListResponse(
        models=["ARIMA", "SARIMA"],
        examples={
            "ARIMA": "ARIMA(2,1,1)",
            "SARIMA": "SARIMA(1,1,1)(1,1,1,12)",
            "带参数的ARIMA": "ARIMA(2,1,1) with ar_params=[0.5, -0.3], ma_params=[0.2]"
        }
    )

@router.get("/models/validate/{model_string}", summary="验证模型字符串")
async def validate_model_string(model_string: str):
    """
    验证模型字符串格式是否正确
    
    Args:
        model_string: 模型字符串
        
    Returns:
        dict: 验证结果
    """
    try:
        # 这里可以添加模型字符串验证逻辑
        # 暂时简单检查是否包含ARIMA或SARIMA
        if "ARIMA" not in model_string.upper() and "SARIMA" not in model_string.upper():
            raise HTTPException(
                status_code=400,
                detail="模型字符串必须包含ARIMA或SARIMA"
            )
        
        return {
            "valid": True,
            "model_string": model_string,
            "message": "模型字符串格式正确"
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"模型字符串验证失败: {str(e)}"
        )
