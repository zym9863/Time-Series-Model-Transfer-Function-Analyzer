"""
时间序列模型的核心类定义

包含ARIMA模型和季节性ARIMA模型的参数化表示、验证和基础数学结构。
"""

from typing import Optional, Tuple, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import numpy as np
from sympy import symbols, Poly, Symbol


class ARIMAModel(BaseModel):
    """
    ARIMA(p, d, q)模型的参数化表示
    
    Attributes:
        p: 自回归阶数 (AR order)
        d: 差分阶数 (Integration order) 
        q: 移动平均阶数 (MA order)
        ar_params: 自回归参数 [φ₁, φ₂, ..., φₚ]
        ma_params: 移动平均参数 [θ₁, θ₂, ..., θₑ]
        constant: 常数项
        name: 模型名称
    """
    
    p: int = Field(ge=0, description="自回归阶数")
    d: int = Field(ge=0, description="差分阶数")
    q: int = Field(ge=0, description="移动平均阶数")
    
    ar_params: Optional[List[Union[float, str]]] = Field(
        default=None,
        description="自回归参数，长度应等于p"
    )
    ma_params: Optional[List[Union[float, str]]] = Field(
        default=None,
        description="移动平均参数，长度应等于q"
    )
    constant: float = Field(default=0.0, description="常数项")
    name: Optional[str] = Field(default=None, description="模型名称")
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    @field_validator('ar_params')
    @classmethod
    def validate_ar_params(cls, v, info):
        """验证自回归参数"""
        if v is not None and info.data:
            p = info.data.get('p', 0)
            if len(v) != p:
                raise ValueError(f"自回归参数长度({len(v)})必须等于p({p})")
        return v

    @field_validator('ma_params')
    @classmethod
    def validate_ma_params(cls, v, info):
        """验证移动平均参数"""
        if v is not None and info.data:
            q = info.data.get('q', 0)
            if len(v) != q:
                raise ValueError(f"移动平均参数长度({len(v)})必须等于q({q})")
        return v

    @model_validator(mode='before')
    @classmethod
    def validate_model(cls, values):
        """模型整体验证"""
        if isinstance(values, dict):
            p, d, q = values.get('p', 0), values.get('d', 0), values.get('q', 0)

            # 只对纯ARIMA模型检查，SARIMA模型有自己的验证逻辑
            if cls.__name__ == 'ARIMAModel' and p == 0 and d == 0 and q == 0:
                raise ValueError("p, d, q不能全为0")

            # 如果没有提供参数，生成默认的符号参数
            if values.get('ar_params') is None and p > 0:
                values['ar_params'] = [f"phi_{i+1}" for i in range(p)]

            if values.get('ma_params') is None and q > 0:
                values['ma_params'] = [f"theta_{i+1}" for i in range(q)]

            # 生成默认名称
            if values.get('name') is None:
                values['name'] = f"ARIMA({p},{d},{q})"

        return values
    
    def get_ar_polynomial(self, lag_operator: Symbol = None) -> Poly:
        """
        获取自回归多项式 φ(B) = 1 - φ₁B - φ₂B² - ... - φₚBᵖ
        
        Args:
            lag_operator: 滞后算子符号，默认为B
            
        Returns:
            自回归多项式
        """
        if lag_operator is None:
            lag_operator = symbols('B')
            
        if self.p == 0:
            return Poly(1, lag_operator)
        
        # 构建多项式系数，注意Poly的系数顺序是从高次项到低次项
        # φ(B) = 1 - φ₁B - φ₂B² - ... - φₚBᵖ
        coeffs = [-float(param) if isinstance(param, (int, float))
                 else -symbols(str(param)) for param in self.ar_params[::-1]] + [1]

        return Poly(coeffs, lag_operator)
    
    def get_ma_polynomial(self, lag_operator: Symbol = None) -> Poly:
        """
        获取移动平均多项式 θ(B) = 1 + θ₁B + θ₂B² + ... + θₑBᵠ
        
        Args:
            lag_operator: 滞后算子符号，默认为B
            
        Returns:
            移动平均多项式
        """
        if lag_operator is None:
            lag_operator = symbols('B')
            
        if self.q == 0:
            return Poly(1, lag_operator)
        
        # 构建多项式系数，注意Poly的系数顺序是从高次项到低次项
        # θ(B) = 1 + θ₁B + θ₂B² + ... + θₑBᵠ
        coeffs = [float(param) if isinstance(param, (int, float))
                 else symbols(str(param)) for param in self.ma_params[::-1]] + [1]

        return Poly(coeffs, lag_operator)
    
    def get_difference_polynomial(self, lag_operator: Symbol = None) -> Poly:
        """
        获取差分多项式 (1-B)ᵈ
        
        Args:
            lag_operator: 滞后算子符号，默认为B
            
        Returns:
            差分多项式
        """
        if lag_operator is None:
            lag_operator = symbols('B')
            
        if self.d == 0:
            return Poly(1, lag_operator)
        
        # (1-B)^d
        base_poly = Poly([1, -1], lag_operator)  # 1 - B
        result = base_poly
        
        for _ in range(self.d - 1):
            result = result * base_poly
            
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "model_type": "ARIMA",
            "parameters": {
                "p": self.p,
                "d": self.d, 
                "q": self.q
            },
            "ar_params": self.ar_params,
            "ma_params": self.ma_params,
            "constant": self.constant,
            "name": self.name
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.name}: AR({self.p}), I({self.d}), MA({self.q})"


class SeasonalARIMAModel(ARIMAModel):
    """
    季节性ARIMA模型 SARIMA(p,d,q)(P,D,Q,m)
    
    继承自ARIMAModel，增加季节性参数
    """
    
    # 季节性参数
    P: int = Field(ge=0, description="季节性自回归阶数")
    D: int = Field(ge=0, description="季节性差分阶数")
    Q: int = Field(ge=0, description="季节性移动平均阶数")
    m: int = Field(gt=0, description="季节性周期")
    
    # 季节性系数
    seasonal_ar_params: Optional[List[Union[float, str]]] = Field(
        default=None,
        description="季节性自回归参数"
    )
    seasonal_ma_params: Optional[List[Union[float, str]]] = Field(
        default=None,
        description="季节性移动平均参数"
    )
    
    @field_validator('seasonal_ar_params')
    @classmethod
    def validate_seasonal_ar_params(cls, v, info):
        """验证季节性自回归参数"""
        if v is not None and info.data:
            P = info.data.get('P', 0)
            if len(v) != P:
                raise ValueError(f"季节性自回归参数长度({len(v)})必须等于P({P})")
        return v

    @field_validator('seasonal_ma_params')
    @classmethod
    def validate_seasonal_ma_params(cls, v, info):
        """验证季节性移动平均参数"""
        if v is not None and info.data:
            Q = info.data.get('Q', 0)
            if len(v) != Q:
                raise ValueError(f"季节性移动平均参数长度({len(v)})必须等于Q({Q})")
        return v

    @model_validator(mode='before')
    @classmethod
    def validate_seasonal_model(cls, values):
        """季节性模型验证"""
        if isinstance(values, dict):
            p, d, q = values.get('p', 0), values.get('d', 0), values.get('q', 0)
            P, D, Q, m = values.get('P', 0), values.get('D', 0), values.get('Q', 0), values.get('m', 1)

            # 对于SARIMA模型，允许非季节性部分全为0，但至少要有一个季节性参数不为0
            if p == 0 and d == 0 and q == 0 and P == 0 and D == 0 and Q == 0:
                raise ValueError("SARIMA模型的所有参数不能全为0")

            # 生成默认的非季节性参数
            if values.get('ar_params') is None and p > 0:
                values['ar_params'] = [f"phi_{i+1}" for i in range(p)]

            if values.get('ma_params') is None and q > 0:
                values['ma_params'] = [f"theta_{i+1}" for i in range(q)]

            # 生成默认季节性参数
            if values.get('seasonal_ar_params') is None and P > 0:
                values['seasonal_ar_params'] = [f"Phi_{i+1}" for i in range(P)]

            if values.get('seasonal_ma_params') is None and Q > 0:
                values['seasonal_ma_params'] = [f"Theta_{i+1}" for i in range(Q)]

            # 更新模型名称
            values['name'] = f"SARIMA({p},{d},{q})({P},{D},{Q},{m})"

        return values
    
    def get_seasonal_ar_polynomial(self, lag_operator: Symbol = None) -> Poly:
        """获取季节性自回归多项式"""
        if lag_operator is None:
            lag_operator = symbols('B')
            
        if self.P == 0:
            return Poly(1, lag_operator)
        
        # Φ(B^m) = 1 - Φ₁B^m - Φ₂B^(2m) - ... - ΦₚB^(Pm)
        coeffs = {}
        coeffs[0] = 1  # 常数项
        
        for i, param in enumerate(self.seasonal_ar_params):
            power = (i + 1) * self.m
            coeff = -float(param) if isinstance(param, (int, float)) else -symbols(str(param))
            coeffs[power] = coeff
        
        # 创建多项式
        max_power = max(coeffs.keys()) if coeffs else 0
        poly_coeffs = [coeffs.get(i, 0) for i in range(max_power + 1)]
        
        return Poly(poly_coeffs, lag_operator)
    
    def get_seasonal_ma_polynomial(self, lag_operator: Symbol = None) -> Poly:
        """获取季节性移动平均多项式"""
        if lag_operator is None:
            lag_operator = symbols('B')
            
        if self.Q == 0:
            return Poly(1, lag_operator)
        
        # Θ(B^m) = 1 + Θ₁B^m + Θ₂B^(2m) + ... + ΘₑB^(Qm)
        coeffs = {}
        coeffs[0] = 1  # 常数项
        
        for i, param in enumerate(self.seasonal_ma_params):
            power = (i + 1) * self.m
            coeff = float(param) if isinstance(param, (int, float)) else symbols(str(param))
            coeffs[power] = coeff
        
        # 创建多项式
        max_power = max(coeffs.keys()) if coeffs else 0
        poly_coeffs = [coeffs.get(i, 0) for i in range(max_power + 1)]
        
        return Poly(poly_coeffs, lag_operator)
    
    def get_seasonal_difference_polynomial(self, lag_operator: Symbol = None) -> Poly:
        """获取季节性差分多项式 (1-B^m)^D"""
        if lag_operator is None:
            lag_operator = symbols('B')
            
        if self.D == 0:
            return Poly(1, lag_operator)
        
        # (1-B^m)^D
        coeffs = [0] * (self.m + 1)
        coeffs[0] = 1    # 1
        coeffs[self.m] = -1  # -B^m
        
        base_poly = Poly(coeffs, lag_operator)
        result = base_poly
        
        for _ in range(self.D - 1):
            result = result * base_poly
            
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        base_dict = super().to_dict()
        base_dict.update({
            "model_type": "SARIMA",
            "seasonal_parameters": {
                "P": self.P,
                "D": self.D,
                "Q": self.Q,
                "m": self.m
            },
            "seasonal_ar_params": self.seasonal_ar_params,
            "seasonal_ma_params": self.seasonal_ma_params
        })
        return base_dict
