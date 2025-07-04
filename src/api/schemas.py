"""
API请求和响应数据模型
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

class ModelType(str, Enum):
    """模型类型枚举"""
    ARIMA = "ARIMA"
    SARIMA = "SARIMA"

class ComplexNumber(BaseModel):
    """复数表示"""
    real: float = Field(description="实部")
    imag: float = Field(description="虚部")

# 请求模型
class ARIMARequest(BaseModel):
    """ARIMA模型分析请求"""
    p: int = Field(ge=0, description="自回归阶数")
    d: int = Field(ge=0, description="差分阶数") 
    q: int = Field(ge=0, description="移动平均阶数")
    ar_params: Optional[List[float]] = Field(default=None, description="自回归参数")
    ma_params: Optional[List[float]] = Field(default=None, description="移动平均参数")
    constant: float = Field(default=0.0, description="常数项")
    name: Optional[str] = Field(default=None, description="模型名称")
    
    # 分析选项
    include_stability: bool = Field(default=True, description="是否包含稳定性分析")
    include_impulse: bool = Field(default=False, description="是否包含脉冲响应")
    include_frequency: bool = Field(default=False, description="是否包含频率响应")
    max_lag: int = Field(default=20, ge=1, description="脉冲响应最大滞后")
    frequencies: Optional[List[float]] = Field(default=None, description="频率列表")

class SARIMARequest(ARIMARequest):
    """SARIMA模型分析请求"""
    P: int = Field(ge=0, description="季节性自回归阶数")
    D: int = Field(ge=0, description="季节性差分阶数")
    Q: int = Field(ge=0, description="季节性移动平均阶数")
    m: int = Field(gt=0, description="季节性周期")
    seasonal_ar_params: Optional[List[float]] = Field(default=None, description="季节性自回归参数")
    seasonal_ma_params: Optional[List[float]] = Field(default=None, description="季节性移动平均参数")

class ModelStringRequest(BaseModel):
    """模型字符串分析请求"""
    model_string: str = Field(description="模型字符串，如'ARIMA(2,1,1)'")
    include_stability: bool = Field(default=True, description="是否包含稳定性分析")
    include_impulse: bool = Field(default=False, description="是否包含脉冲响应")
    include_frequency: bool = Field(default=False, description="是否包含频率响应")
    max_lag: int = Field(default=20, ge=1, description="脉冲响应最大滞后")
    frequencies: Optional[List[float]] = Field(default=None, description="频率列表")

# 响应模型
class ModelInfo(BaseModel):
    """模型信息"""
    model_type: str = Field(description="模型类型")
    parameters: Dict[str, Any] = Field(description="模型参数")
    name: str = Field(description="模型名称")

class TransferFunctionInfo(BaseModel):
    """传递函数信息"""
    numerator: str = Field(description="分子多项式")
    denominator: str = Field(description="分母多项式")
    poles: List[ComplexNumber] = Field(description="极点")
    zeros: List[ComplexNumber] = Field(description="零点")

class StabilityInfo(BaseModel):
    """稳定性分析信息"""
    is_stable: bool = Field(description="是否稳定")
    max_pole_magnitude: float = Field(description="最大极点模长")
    stability_margin: float = Field(description="稳定性裕度")

class ImpulseResponse(BaseModel):
    """脉冲响应"""
    lag: int = Field(description="滞后期")
    value: float = Field(description="响应值")

class FrequencyResponse(BaseModel):
    """频率响应"""
    frequency: float = Field(description="频率")
    magnitude: float = Field(description="幅度")
    phase: float = Field(description="相位")

class AnalysisResponse(BaseModel):
    """分析结果响应"""
    model: ModelInfo = Field(description="模型信息")
    transfer_function: TransferFunctionInfo = Field(description="传递函数")
    stability: Optional[StabilityInfo] = Field(default=None, description="稳定性分析")
    impulse_response: Optional[List[ImpulseResponse]] = Field(default=None, description="脉冲响应")
    frequency_response: Optional[List[FrequencyResponse]] = Field(default=None, description="频率响应")

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(description="错误信息")
    status_code: int = Field(description="状态码")
    details: Optional[Any] = Field(default=None, description="详细信息")

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(description="服务状态")
    version: str = Field(description="版本号")
    timestamp: str = Field(description="时间戳")

class ModelListResponse(BaseModel):
    """模型列表响应"""
    models: List[str] = Field(description="支持的模型类型")
    examples: Dict[str, str] = Field(description="示例模型字符串")
