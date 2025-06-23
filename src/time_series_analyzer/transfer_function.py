"""
传递函数推导引擎

基于符号计算自动推导ARIMA模型的传递函数表达式。
将时间序列模型转换为关于滞后算子B的多项式比值形式。
"""

from typing import Dict, Any, Optional, Tuple
from sympy import symbols, Poly, simplify, factor, expand, Symbol, Rational
from sympy.polys.polyfuncs import interpolate
import sympy as sp

from .models import ARIMAModel, SeasonalARIMAModel


class TransferFunction:
    """
    传递函数表示类
    
    表示形式: H(B) = numerator(B) / denominator(B)
    其中B是滞后算子
    """
    
    def __init__(self, numerator: Poly, denominator: Poly, lag_operator: Symbol = None):
        """
        初始化传递函数
        
        Args:
            numerator: 分子多项式
            denominator: 分母多项式  
            lag_operator: 滞后算子符号
        """
        if lag_operator is None:
            lag_operator = symbols('B')
            
        self.lag_operator = lag_operator
        self.numerator = numerator
        self.denominator = denominator
        
        # 简化传递函数
        self._simplify()
    
    def _simplify(self):
        """简化传递函数，约去公因子"""
        try:
            # 计算最大公约数
            gcd_poly = sp.gcd(self.numerator.as_expr(), self.denominator.as_expr())
            
            if gcd_poly != 1:
                # 约去公因子
                self.numerator = Poly(
                    simplify(self.numerator.as_expr() / gcd_poly), 
                    self.lag_operator
                )
                self.denominator = Poly(
                    simplify(self.denominator.as_expr() / gcd_poly),
                    self.lag_operator
                )
        except Exception:            # 如果简化失败，保持原样
            pass
    
    def evaluate_at_frequency(self, frequency: complex) -> complex:
        """
        在特定频率处计算传递函数值
        
        Args:
            frequency: 频率值 (通常是 e^{-iω})
            
        Returns:
            传递函数在该频率处的值
        """
        num_expr = self.numerator.as_expr().subs(self.lag_operator, frequency)
        den_expr = self.denominator.as_expr().subs(self.lag_operator, frequency)
        
        # 确保结果为数值
        num_val = complex(num_expr.evalf())
        den_val = complex(den_expr.evalf())
        
        if abs(den_val) < 1e-12:
            raise ValueError(f"分母在频率{frequency}处为零")
            
        return num_val / den_val
    
    def get_poles(self) -> list:
        """获取传递函数的极点（分母的根）"""
        try:
            roots = sp.solve(self.denominator.as_expr(), self.lag_operator)
            return [complex(root.evalf()) for root in roots if root.is_finite]
        except Exception:
            return []
    
    def get_zeros(self) -> list:
        """获取传递函数的零点（分子的根）"""
        try:
            roots = sp.solve(self.numerator.as_expr(), self.lag_operator)
            return [complex(root.evalf()) for root in roots if root.is_finite]
        except Exception:
            return []
    
    def is_stable(self) -> bool:
        """
        检查系统稳定性
        对于离散时间系统，所有极点的模长应小于1
        """
        poles = self.get_poles()
        return all(abs(pole) < 1 for pole in poles)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"H({self.lag_operator}) = ({self.numerator.as_expr()}) / ({self.denominator.as_expr()})"
    
    def __repr__(self) -> str:
        return self.__str__()


class TransferFunctionDeriver:
    """
    传递函数推导器
    
    将ARIMA模型自动转换为传递函数形式
    """
    
    def __init__(self, lag_operator: Symbol = None):
        """
        初始化推导器
        
        Args:
            lag_operator: 滞后算子符号，默认为B
        """
        if lag_operator is None:
            lag_operator = symbols('B')
        self.lag_operator = lag_operator
    
    def derive_arima_transfer_function(self, model: ARIMAModel) -> TransferFunction:
        """
        推导ARIMA模型的传递函数
        
        ARIMA(p,d,q)模型的一般形式:
        φ(B)(1-B)^d X_t = θ(B)ε_t
        
        传递函数: H(B) = θ(B) / [φ(B)(1-B)^d]
        
        Args:
            model: ARIMA模型
            
        Returns:
            传递函数对象
        """
        # 获取各个多项式
        ar_poly = model.get_ar_polynomial(self.lag_operator)
        ma_poly = model.get_ma_polynomial(self.lag_operator)
        diff_poly = model.get_difference_polynomial(self.lag_operator)
        
        # 分子：移动平均多项式 θ(B)
        numerator = ma_poly
        
        # 分母：自回归多项式 × 差分多项式 φ(B)(1-B)^d
        denominator = ar_poly * diff_poly
        
        return TransferFunction(numerator, denominator, self.lag_operator)
    
    def derive_sarima_transfer_function(self, model: SeasonalARIMAModel) -> TransferFunction:
        """
        推导季节性ARIMA模型的传递函数
        
        SARIMA(p,d,q)(P,D,Q,m)模型的一般形式:
        φ(B)Φ(B^m)(1-B)^d(1-B^m)^D X_t = θ(B)Θ(B^m)ε_t
        
        传递函数: H(B) = θ(B)Θ(B^m) / [φ(B)Φ(B^m)(1-B)^d(1-B^m)^D]
        
        Args:
            model: 季节性ARIMA模型
            
        Returns:
            传递函数对象
        """
        # 获取非季节性多项式
        ar_poly = model.get_ar_polynomial(self.lag_operator)
        ma_poly = model.get_ma_polynomial(self.lag_operator)
        diff_poly = model.get_difference_polynomial(self.lag_operator)
        
        # 获取季节性多项式
        seasonal_ar_poly = model.get_seasonal_ar_polynomial(self.lag_operator)
        seasonal_ma_poly = model.get_seasonal_ma_polynomial(self.lag_operator)
        seasonal_diff_poly = model.get_seasonal_difference_polynomial(self.lag_operator)
        
        # 分子：θ(B)Θ(B^m)
        numerator = ma_poly * seasonal_ma_poly
        
        # 分母：φ(B)Φ(B^m)(1-B)^d(1-B^m)^D
        denominator = ar_poly * seasonal_ar_poly * diff_poly * seasonal_diff_poly
        
        return TransferFunction(numerator, denominator, self.lag_operator)
    
    def derive_transfer_function(self, model) -> TransferFunction:
        """
        通用传递函数推导方法
        
        Args:
            model: ARIMA或SARIMA模型
            
        Returns:
            传递函数对象
        """
        if isinstance(model, SeasonalARIMAModel):
            return self.derive_sarima_transfer_function(model)
        elif isinstance(model, ARIMAModel):
            return self.derive_arima_transfer_function(model)
        else:
            raise ValueError(f"不支持的模型类型: {type(model)}")
    
    def derive_impulse_response(self, model, max_lag: int = 20) -> Dict[int, Any]:
        """
        推导脉冲响应函数
        
        通过传递函数的幂级数展开获得脉冲响应系数
        
        Args:
            model: 时间序列模型
            max_lag: 最大滞后阶数
            
        Returns:
            脉冲响应系数字典 {lag: coefficient}
        """
        transfer_func = self.derive_transfer_function(model)
        
        # 计算幂级数展开
        try:
            # H(B) = num(B) / den(B) = Σ h_j B^j
            num_expr = transfer_func.numerator.as_expr()
            den_expr = transfer_func.denominator.as_expr()
            
            # 使用sympy的series展开
            series = sp.series(num_expr / den_expr, self.lag_operator, 0, max_lag + 1)
            
            impulse_response = {}
            for i in range(max_lag + 1):
                coeff = series.coeff(self.lag_operator, i)
                if coeff is not None:
                    impulse_response[i] = coeff
                else:
                    impulse_response[i] = 0
                    
            return impulse_response
            
        except Exception as e:
            # 如果符号计算失败，返回空字典
            return {}
    
    def analyze_stability(self, model) -> Dict[str, Any]:
        """
        分析模型稳定性
        
        Args:
            model: 时间序列模型
            
        Returns:
            稳定性分析结果
        """
        transfer_func = self.derive_transfer_function(model)
        
        poles = transfer_func.get_poles()
        zeros = transfer_func.get_zeros()
        is_stable = transfer_func.is_stable()
        
        # 计算极点的模长
        pole_magnitudes = [abs(pole) for pole in poles]
        
        return {
            "is_stable": is_stable,
            "poles": poles,
            "zeros": zeros,            "pole_magnitudes": pole_magnitudes,
            "max_pole_magnitude": max(pole_magnitudes) if pole_magnitudes else 0,
            "stability_margin": 1 - max(pole_magnitudes) if pole_magnitudes else 1
        }

    def get_frequency_response(self, model, frequencies: list, 
                             param_values: dict = None) -> Dict[str, list]:
        """
        计算频率响应
        
        Args:
            model: 时间序列模型
            frequencies: 频率列表 (弧度)
            param_values: 模型参数的数值，格式为 {'phi_1': 0.5, 'theta_1': 0.3, ...}
                         如果为None，将使用默认值
            
        Returns:
            频率响应数据
        """
        import math
        transfer_func = self.derive_transfer_function(model)
        
        # 如果没有提供参数值，使用默认值
        if param_values is None:
            param_values = self._get_default_params(model)
        
        magnitudes = []
        phases = []
        
        for omega in frequencies:
            # 计算 e^{-iω}
            z = complex(math.cos(omega), -math.sin(omega))
            
            try:
                response = self._evaluate_with_params(transfer_func, z, param_values)
                magnitudes.append(abs(response))
                phases.append(math.atan2(response.imag, response.real))
            except (ValueError, TypeError):
                magnitudes.append(float('inf'))
                phases.append(0)
        
        return {
            "frequencies": frequencies,
            "magnitudes": magnitudes,
            "phases": phases,
            "magnitude_db": [20 * math.log10(mag) if mag > 0 and math.isfinite(mag) else -float('inf') 
                           for mag in magnitudes]
        }
    
    def _get_default_params(self, model) -> dict:
        """获取模型的默认参数值"""
        params = {}
        
        # AR参数：使用稳定值
        if hasattr(model, 'ar_params') and model.ar_params:
            for i, param in enumerate(model.ar_params):
                if isinstance(param, str):
                    # 为了稳定性，AR参数应该较小
                    params[param] = 0.1 * (i + 1)
                    
        # MA参数：使用适中值
        if hasattr(model, 'ma_params') and model.ma_params:
            for i, param in enumerate(model.ma_params):
                if isinstance(param, str):
                    params[param] = 0.2 * (i + 1)
                    
        # 季节性参数
        if hasattr(model, 'seasonal_ar_params') and model.seasonal_ar_params:
            for i, param in enumerate(model.seasonal_ar_params):
                if isinstance(param, str):
                    params[param] = 0.05 * (i + 1)
                    
        if hasattr(model, 'seasonal_ma_params') and model.seasonal_ma_params:
            for i, param in enumerate(model.seasonal_ma_params):
                if isinstance(param, str):
                    params[param] = 0.1 * (i + 1)
        
        return params
    
    def _evaluate_with_params(self, transfer_func: TransferFunction, 
                            frequency: complex, param_values: dict) -> complex:
        """使用给定参数值计算传递函数在特定频率的值"""
        # 获取分子和分母表达式
        num_expr = transfer_func.numerator.as_expr()
        den_expr = transfer_func.denominator.as_expr()
        
        # 替换滞后算子
        num_expr = num_expr.subs(transfer_func.lag_operator, frequency)
        den_expr = den_expr.subs(transfer_func.lag_operator, frequency)
        
        # 替换参数
        for param_name, param_value in param_values.items():
            num_expr = num_expr.subs(symbols(param_name), param_value)
            den_expr = den_expr.subs(symbols(param_name), param_value)
        
        # 计算数值
        num_val = complex(num_expr.evalf())
        den_val = complex(den_expr.evalf())
        
        if abs(den_val) < 1e-12:
            raise ValueError(f"分母在频率{frequency}处为零")
            
        return num_val / den_val
