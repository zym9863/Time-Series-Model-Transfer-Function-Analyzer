"""
时序模型传递函数分析器

一个用于自动推导时间序列模型传递函数的Python库。
支持ARIMA模型的参数化输入和传递函数的符号推导。
"""

from .models import ARIMAModel, SeasonalARIMAModel
from .transfer_function import TransferFunction, TransferFunctionDeriver
from .parsers import ModelParser
from .formatters import OutputFormatter
from .api import TimeSeriesAnalyzer, analyze_arima, analyze_sarima, parse_and_analyze

__version__ = "0.1.0"
__author__ = "zym"
__email__ = "ym214413520@gmail.com"

__all__ = [
    "ARIMAModel",
    "SeasonalARIMAModel",
    "TransferFunction",
    "TransferFunctionDeriver",
    "ModelParser",
    "OutputFormatter",
    "TimeSeriesAnalyzer",
    "analyze_arima",
    "analyze_sarima",
    "parse_and_analyze",
]
