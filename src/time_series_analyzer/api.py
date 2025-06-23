"""
Python库API接口

提供简洁易用的Python API，方便其他项目集成使用。
"""

from typing import Dict, Any, Optional, Union, List, Tuple
from pathlib import Path

from .models import ARIMAModel, SeasonalARIMAModel
from .transfer_function import TransferFunction, TransferFunctionDeriver
from .parsers import ModelParser
from .formatters import OutputFormatter


class TimeSeriesAnalyzer:
    """
    时间序列模型分析器主类
    
    提供统一的API接口用于ARIMA/SARIMA模型的传递函数分析。
    """
    
    def __init__(self, precision: int = 4):
        """
        初始化分析器
        
        Args:
            precision: 数值精度
        """
        self.precision = precision
        self.deriver = TransferFunctionDeriver()
        self.formatter = OutputFormatter(precision=precision)
    
    def create_arima_model(self, p: int, d: int, q: int,
                          ar_params: Optional[List[float]] = None,
                          ma_params: Optional[List[float]] = None,
                          constant: float = 0.0,
                          name: Optional[str] = None) -> ARIMAModel:
        """
        创建ARIMA模型
        
        Args:
            p: 自回归阶数
            d: 差分阶数
            q: 移动平均阶数
            ar_params: 自回归参数
            ma_params: 移动平均参数
            constant: 常数项
            name: 模型名称
            
        Returns:
            ARIMA模型对象
        """
        return ARIMAModel(
            p=p, d=d, q=q,
            ar_params=ar_params,
            ma_params=ma_params,
            constant=constant,
            name=name
        )
    
    def create_sarima_model(self, p: int, d: int, q: int,
                           P: int, D: int, Q: int, m: int,
                           ar_params: Optional[List[float]] = None,
                           ma_params: Optional[List[float]] = None,
                           seasonal_ar_params: Optional[List[float]] = None,
                           seasonal_ma_params: Optional[List[float]] = None,
                           constant: float = 0.0,
                           name: Optional[str] = None) -> SeasonalARIMAModel:
        """
        创建SARIMA模型
        
        Args:
            p, d, q: 非季节性参数
            P, D, Q, m: 季节性参数
            ar_params: 自回归参数
            ma_params: 移动平均参数
            seasonal_ar_params: 季节性自回归参数
            seasonal_ma_params: 季节性移动平均参数
            constant: 常数项
            name: 模型名称
            
        Returns:
            SARIMA模型对象
        """
        return SeasonalARIMAModel(
            p=p, d=d, q=q,
            P=P, D=D, Q=Q, m=m,
            ar_params=ar_params,
            ma_params=ma_params,
            seasonal_ar_params=seasonal_ar_params,
            seasonal_ma_params=seasonal_ma_params,
            constant=constant,
            name=name
        )
    
    def parse_model_string(self, model_str: str) -> Union[ARIMAModel, SeasonalARIMAModel]:
        """
        从字符串解析模型
        
        Args:
            model_str: 模型字符串，如 "ARIMA(2,1,1)" 或 "SARIMA(2,1,1)(1,1,1,12)"
            
        Returns:
            模型对象
        """
        return ModelParser.parse_from_string(model_str)
    
    def load_model_from_file(self, file_path: Union[str, Path]) -> Union[ARIMAModel, SeasonalARIMAModel]:
        """
        从文件加载模型
        
        Args:
            file_path: 配置文件路径 (JSON/YAML)
            
        Returns:
            模型对象
        """
        return ModelParser.parse_from_file(file_path)
    
    def derive_transfer_function(self, model: Union[ARIMAModel, SeasonalARIMAModel]) -> TransferFunction:
        """
        推导传递函数
        
        Args:
            model: 时间序列模型
            
        Returns:
            传递函数对象
        """
        return self.deriver.derive_transfer_function(model)
    
    def analyze_stability(self, model: Union[ARIMAModel, SeasonalARIMAModel]) -> Dict[str, Any]:
        """
        分析模型稳定性
        
        Args:
            model: 时间序列模型
            
        Returns:
            稳定性分析结果
        """
        return self.deriver.analyze_stability(model)
    
    def compute_impulse_response(self, model: Union[ARIMAModel, SeasonalARIMAModel],
                                max_lag: int = 20) -> Dict[int, Any]:
        """
        计算脉冲响应函数
        
        Args:
            model: 时间序列模型
            max_lag: 最大滞后阶数
            
        Returns:
            脉冲响应系数字典
        """
        return self.deriver.derive_impulse_response(model, max_lag)
    
    def compute_frequency_response(self, model: Union[ARIMAModel, SeasonalARIMAModel],
                                  frequencies: List[float]) -> Dict[str, List]:
        """
        计算频率响应
        
        Args:
            model: 时间序列模型
            frequencies: 频率列表
            
        Returns:
            频率响应数据
        """
        return self.deriver.get_frequency_response(model, frequencies)
    
    def generate_report(self, model: Union[ARIMAModel, SeasonalARIMAModel],
                       format: str = 'text',
                       include_analysis: bool = True,
                       output_file: Optional[Union[str, Path]] = None) -> str:
        """
        生成分析报告
        
        Args:
            model: 时间序列模型
            format: 输出格式 ('text', 'latex', 'json')
            include_analysis: 是否包含稳定性分析
            output_file: 输出文件路径
            
        Returns:
            报告内容
        """
        if format.lower() == 'latex':
            content = self.formatter.format_latex(
                model, 
                include_transfer_function=True,
                include_analysis=include_analysis
            )
        elif format.lower() == 'json':
            content = self.formatter.format_json(
                model,
                include_transfer_function=True,
                include_analysis=include_analysis
            )
        else:  # text
            content = self.formatter.format_plain_text(
                model,
                include_transfer_function=True,
                include_analysis=include_analysis
            )
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return content
    
    def quick_analyze(self, model_str: str, 
                     include_stability: bool = True,
                     include_impulse: bool = False,
                     include_frequency: bool = False,
                     max_lag: int = 20,
                     frequencies: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        快速分析接口
        
        Args:
            model_str: 模型字符串
            include_stability: 是否包含稳定性分析
            include_impulse: 是否包含脉冲响应
            include_frequency: 是否包含频率响应
            max_lag: 脉冲响应最大滞后
            frequencies: 频率列表
            
        Returns:
            完整分析结果
        """
        # 解析模型
        model = self.parse_model_string(model_str)
        
        # 推导传递函数
        transfer_func = self.derive_transfer_function(model)
        
        result = {
            "model": model.to_dict(),
            "transfer_function": {
                "numerator": str(transfer_func.numerator.as_expr()),
                "denominator": str(transfer_func.denominator.as_expr()),
                "poles": [{"real": pole.real, "imag": pole.imag} for pole in transfer_func.get_poles()],
                "zeros": [{"real": zero.real, "imag": zero.imag} for zero in transfer_func.get_zeros()]
            }
        }
        
        # 稳定性分析
        if include_stability:
            stability = self.analyze_stability(model)
            result["stability"] = {
                "is_stable": stability["is_stable"],
                "max_pole_magnitude": stability["max_pole_magnitude"],
                "stability_margin": stability["stability_margin"]
            }
        
        # 脉冲响应
        if include_impulse:
            impulse_response = self.compute_impulse_response(model, max_lag)
            result["impulse_response"] = {str(k): str(v) for k, v in impulse_response.items()}
        
        # 频率响应
        if include_frequency:
            if frequencies is None:
                frequencies = [i * 0.1 for i in range(6)]  # 0, 0.1, 0.2, 0.3, 0.4, 0.5
            
            freq_response = self.compute_frequency_response(model, frequencies)
            result["frequency_response"] = {
                "frequencies": freq_response["frequencies"],
                "magnitudes": [float(m) for m in freq_response["magnitudes"]],
                "phases": [float(p) for p in freq_response["phases"]]
            }
        
        return result


# 便捷函数
def analyze_arima(p: int, d: int, q: int,
                 ar_params: Optional[List[float]] = None,
                 ma_params: Optional[List[float]] = None,
                 **kwargs) -> Dict[str, Any]:
    """
    快速分析ARIMA模型的便捷函数
    
    Args:
        p, d, q: ARIMA参数
        ar_params: 自回归参数
        ma_params: 移动平均参数
        **kwargs: 其他分析选项
        
    Returns:
        分析结果
    """
    analyzer = TimeSeriesAnalyzer()
    model = analyzer.create_arima_model(p, d, q, ar_params, ma_params)
    
    return analyzer.quick_analyze(
        str(model).split(':')[0],  # 提取模型字符串
        **kwargs
    )


def analyze_sarima(p: int, d: int, q: int, P: int, D: int, Q: int, m: int,
                  ar_params: Optional[List[float]] = None,
                  ma_params: Optional[List[float]] = None,
                  seasonal_ar_params: Optional[List[float]] = None,
                  seasonal_ma_params: Optional[List[float]] = None,
                  **kwargs) -> Dict[str, Any]:
    """
    快速分析SARIMA模型的便捷函数
    
    Args:
        p, d, q, P, D, Q, m: SARIMA参数
        ar_params: 自回归参数
        ma_params: 移动平均参数
        seasonal_ar_params: 季节性自回归参数
        seasonal_ma_params: 季节性移动平均参数
        **kwargs: 其他分析选项
        
    Returns:
        分析结果
    """
    analyzer = TimeSeriesAnalyzer()
    model = analyzer.create_sarima_model(
        p, d, q, P, D, Q, m,
        ar_params, ma_params,
        seasonal_ar_params, seasonal_ma_params
    )
    
    return analyzer.quick_analyze(
        str(model).split(':')[0],  # 提取模型字符串
        **kwargs
    )


def parse_and_analyze(model_str: str, **kwargs) -> Dict[str, Any]:
    """
    解析模型字符串并分析的便捷函数
    
    Args:
        model_str: 模型字符串
        **kwargs: 分析选项
        
    Returns:
        分析结果
    """
    analyzer = TimeSeriesAnalyzer()
    return analyzer.quick_analyze(model_str, **kwargs)
