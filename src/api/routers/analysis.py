"""
分析服务路由
"""

import math
from typing import List
from fastapi import APIRouter, HTTPException
from ...time_series_analyzer import TimeSeriesAnalyzer
from ..schemas import (
    ARIMARequest, SARIMARequest, ModelStringRequest,
    AnalysisResponse, ModelInfo, TransferFunctionInfo,
    StabilityInfo, ImpulseResponse, FrequencyResponse,
    ComplexNumber
)

router = APIRouter()

def convert_complex_to_schema(complex_num) -> ComplexNumber:
    """将复数转换为schema格式"""
    return ComplexNumber(real=float(complex_num.real), imag=float(complex_num.imag))

def build_analysis_response(analyzer: TimeSeriesAnalyzer, model, 
                          include_stability: bool = True,
                          include_impulse: bool = False,
                          include_frequency: bool = False,
                          max_lag: int = 20,
                          frequencies: List[float] = None) -> AnalysisResponse:
    """构建分析响应"""
    
    # 推导传递函数
    transfer_func = analyzer.derive_transfer_function(model)
    
    # 基础模型信息
    model_dict = model.to_dict()
    model_info = ModelInfo(
        model_type=model_dict["model_type"],
        parameters=model_dict["parameters"],
        name=model.name or str(model)
    )
    
    # 传递函数信息
    transfer_info = TransferFunctionInfo(
        numerator=str(transfer_func.numerator.as_expr()),
        denominator=str(transfer_func.denominator.as_expr()),
        poles=[convert_complex_to_schema(pole) for pole in transfer_func.get_poles()],
        zeros=[convert_complex_to_schema(zero) for zero in transfer_func.get_zeros()]
    )
    
    # 稳定性分析
    stability_info = None
    if include_stability:
        stability = analyzer.analyze_stability(model)
        stability_info = StabilityInfo(
            is_stable=stability["is_stable"],
            max_pole_magnitude=stability["max_pole_magnitude"],
            stability_margin=stability["stability_margin"]
        )
    
    # 脉冲响应
    impulse_response = None
    if include_impulse:
        impulse_data = analyzer.compute_impulse_response(model, max_lag=max_lag)
        impulse_response = [
            ImpulseResponse(lag=i, value=float(val))
            for i, val in enumerate(impulse_data)
        ]
    
    # 频率响应
    frequency_response = None
    if include_frequency and frequencies:
        freq_data = analyzer.compute_frequency_response(model, frequencies)
        frequency_response = []
        for freq, mag, phase in zip(
            freq_data["frequencies"],
            freq_data["magnitudes"],
            freq_data["phases"]
        ):
            # 处理无穷大和NaN值
            if not math.isfinite(mag):
                mag = 1e6  # 用大数代替无穷大
            if not math.isfinite(phase):
                phase = 0.0

            frequency_response.append(FrequencyResponse(
                frequency=float(freq),
                magnitude=float(mag),
                phase=float(phase)
            ))
    
    return AnalysisResponse(
        model=model_info,
        transfer_function=transfer_info,
        stability=stability_info,
        impulse_response=impulse_response,
        frequency_response=frequency_response
    )

@router.post("/analyze/arima", response_model=AnalysisResponse, summary="分析ARIMA模型")
async def analyze_arima(request: ARIMARequest):
    """
    分析ARIMA模型并返回传递函数等信息
    
    Args:
        request: ARIMA模型分析请求
        
    Returns:
        AnalysisResponse: 完整的分析结果
    """
    try:
        analyzer = TimeSeriesAnalyzer()
        
        # 创建ARIMA模型
        model = analyzer.create_arima_model(
            p=request.p,
            d=request.d,
            q=request.q,
            ar_params=request.ar_params,
            ma_params=request.ma_params,
            constant=request.constant,
            name=request.name
        )
        
        return build_analysis_response(
            analyzer=analyzer,
            model=model,
            include_stability=request.include_stability,
            include_impulse=request.include_impulse,
            include_frequency=request.include_frequency,
            max_lag=request.max_lag,
            frequencies=request.frequencies
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"ARIMA模型分析失败: {str(e)}"
        )

@router.post("/analyze/sarima", response_model=AnalysisResponse, summary="分析SARIMA模型")
async def analyze_sarima(request: SARIMARequest):
    """
    分析SARIMA模型并返回传递函数等信息
    
    Args:
        request: SARIMA模型分析请求
        
    Returns:
        AnalysisResponse: 完整的分析结果
    """
    try:
        analyzer = TimeSeriesAnalyzer()
        
        # 创建SARIMA模型
        model = analyzer.create_sarima_model(
            p=request.p, d=request.d, q=request.q,
            P=request.P, D=request.D, Q=request.Q, m=request.m,
            ar_params=request.ar_params,
            ma_params=request.ma_params,
            seasonal_ar_params=request.seasonal_ar_params,
            seasonal_ma_params=request.seasonal_ma_params,
            constant=request.constant,
            name=request.name
        )
        
        return build_analysis_response(
            analyzer=analyzer,
            model=model,
            include_stability=request.include_stability,
            include_impulse=request.include_impulse,
            include_frequency=request.include_frequency,
            max_lag=request.max_lag,
            frequencies=request.frequencies
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"SARIMA模型分析失败: {str(e)}"
        )

@router.post("/analyze/model-string", response_model=AnalysisResponse, summary="通过模型字符串分析")
async def analyze_model_string(request: ModelStringRequest):
    """
    通过模型字符串分析模型并返回传递函数等信息

    Args:
        request: 模型字符串分析请求

    Returns:
        AnalysisResponse: 完整的分析结果
    """
    try:
        analyzer = TimeSeriesAnalyzer()

        # 解析模型字符串
        model = analyzer.parse_model_string(request.model_string)

        return build_analysis_response(
            analyzer=analyzer,
            model=model,
            include_stability=request.include_stability,
            include_impulse=request.include_impulse,
            include_frequency=request.include_frequency,
            max_lag=request.max_lag,
            frequencies=request.frequencies
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"模型字符串分析失败: {str(e)}"
        )

@router.get("/analyze/transfer-function/{model_string}", summary="仅获取传递函数")
async def get_transfer_function(model_string: str):
    """
    仅获取模型的传递函数表达式

    Args:
        model_string: 模型字符串

    Returns:
        dict: 传递函数信息
    """
    try:
        analyzer = TimeSeriesAnalyzer()
        model = analyzer.parse_model_string(model_string)
        transfer_func = analyzer.derive_transfer_function(model)

        return {
            "model_string": model_string,
            "transfer_function": {
                "numerator": str(transfer_func.numerator.as_expr()),
                "denominator": str(transfer_func.denominator.as_expr()),
                "expression": str(transfer_func)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"传递函数推导失败: {str(e)}"
        )

@router.get("/analyze/stability/{model_string}", summary="仅获取稳定性分析")
async def get_stability_analysis(model_string: str):
    """
    仅获取模型的稳定性分析

    Args:
        model_string: 模型字符串

    Returns:
        dict: 稳定性分析结果
    """
    try:
        analyzer = TimeSeriesAnalyzer()
        model = analyzer.parse_model_string(model_string)
        stability = analyzer.analyze_stability(model)

        # 清理稳定性数据，确保可以JSON序列化
        clean_stability = {
            "is_stable": stability["is_stable"],
            "max_pole_magnitude": float(stability["max_pole_magnitude"]),
            "stability_margin": float(stability["stability_margin"])
        }

        return {
            "model_string": model_string,
            "stability": clean_stability
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"稳定性分析失败: {str(e)}"
        )
