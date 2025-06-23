"""
测试API接口
"""

import pytest
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from time_series_analyzer.api import (
    TimeSeriesAnalyzer, 
    analyze_arima, 
    analyze_sarima, 
    parse_and_analyze
)
from time_series_analyzer.models import ARIMAModel, SeasonalARIMAModel


class TestTimeSeriesAnalyzer:
    """测试时间序列分析器API"""
    
    def test_create_arima_model(self):
        """测试创建ARIMA模型"""
        analyzer = TimeSeriesAnalyzer()
        
        model = analyzer.create_arima_model(
            p=2, d=1, q=1,
            ar_params=[0.5, -0.3],
            ma_params=[0.2]
        )
        
        assert isinstance(model, ARIMAModel)
        assert model.p == 2
        assert model.d == 1
        assert model.q == 1
        assert model.ar_params == [0.5, -0.3]
        assert model.ma_params == [0.2]
    
    def test_create_sarima_model(self):
        """测试创建SARIMA模型"""
        analyzer = TimeSeriesAnalyzer()
        
        model = analyzer.create_sarima_model(
            p=2, d=1, q=1,
            P=1, D=1, Q=1, m=12,
            ar_params=[0.5, -0.3],
            ma_params=[0.2],
            seasonal_ar_params=[0.8],
            seasonal_ma_params=[0.4]
        )
        
        assert isinstance(model, SeasonalARIMAModel)
        assert model.p == 2
        assert model.P == 1
        assert model.m == 12
        assert model.seasonal_ar_params == [0.8]
    
    def test_parse_model_string(self):
        """测试解析模型字符串"""
        analyzer = TimeSeriesAnalyzer()
        
        model = analyzer.parse_model_string("ARIMA(2,1,1)")
        
        assert isinstance(model, ARIMAModel)
        assert model.p == 2
        assert model.d == 1
        assert model.q == 1
    
    def test_derive_transfer_function(self):
        """测试推导传递函数"""
        analyzer = TimeSeriesAnalyzer()
        
        model = analyzer.create_arima_model(
            p=1, d=0, q=1,
            ar_params=[0.5],
            ma_params=[0.2]
        )
        
        tf = analyzer.derive_transfer_function(model)
        
        # 检查传递函数的基本属性
        assert tf.lag_operator.name == 'B'
        assert tf.numerator is not None
        assert tf.denominator is not None
    
    def test_analyze_stability(self):
        """测试稳定性分析"""
        analyzer = TimeSeriesAnalyzer()
        
        # 稳定模型
        stable_model = analyzer.create_arima_model(
            p=1, d=0, q=0,
            ar_params=[0.5]
        )
        
        stability = analyzer.analyze_stability(stable_model)
        
        assert "is_stable" in stability
        assert "poles" in stability
        assert "zeros" in stability
        assert "max_pole_magnitude" in stability
        assert "stability_margin" in stability
        
        assert isinstance(stability["is_stable"], bool)
        assert isinstance(stability["poles"], list)
        assert isinstance(stability["max_pole_magnitude"], (int, float))
    
    def test_compute_impulse_response(self):
        """测试脉冲响应计算"""
        analyzer = TimeSeriesAnalyzer()
        
        model = analyzer.create_arima_model(
            p=0, d=0, q=1,
            ma_params=[0.5]
        )
        
        impulse_response = analyzer.compute_impulse_response(model, max_lag=5)
        
        assert isinstance(impulse_response, dict)
        assert len(impulse_response) == 6  # 0到5
        assert 0 in impulse_response
        assert 1 in impulse_response
    
    def test_compute_frequency_response(self):
        """测试频率响应计算"""
        analyzer = TimeSeriesAnalyzer()
        
        model = analyzer.create_arima_model(
            p=1, d=0, q=0,
            ar_params=[0.5]
        )
        
        frequencies = [0, 0.1, 0.2]
        freq_response = analyzer.compute_frequency_response(model, frequencies)
        
        assert "frequencies" in freq_response
        assert "magnitudes" in freq_response
        assert "phases" in freq_response
        assert "magnitude_db" in freq_response
        
        assert len(freq_response["frequencies"]) == 3
        assert len(freq_response["magnitudes"]) == 3
        assert len(freq_response["phases"]) == 3
    
    def test_generate_report_text(self):
        """测试生成文本报告"""
        analyzer = TimeSeriesAnalyzer()
        
        model = analyzer.create_arima_model(p=2, d=1, q=1)
        
        report = analyzer.generate_report(model, format='text')
        
        assert isinstance(report, str)
        assert "ARIMA(2,1,1)" in report
        assert "传递函数" in report
    
    def test_generate_report_json(self):
        """测试生成JSON报告"""
        analyzer = TimeSeriesAnalyzer()
        
        model = analyzer.create_arima_model(p=2, d=1, q=1)
        
        report = analyzer.generate_report(model, format='json')
        
        assert isinstance(report, str)
        # 验证是否为有效JSON
        import json
        data = json.loads(report)
        assert "model" in data
        assert "transfer_function" in data
    
    def test_quick_analyze(self):
        """测试快速分析接口"""
        analyzer = TimeSeriesAnalyzer()
        
        result = analyzer.quick_analyze(
            "ARIMA(1,0,1)",
            include_stability=True,
            include_impulse=True,
            include_frequency=True,
            max_lag=5
        )
        
        assert "model" in result
        assert "transfer_function" in result
        assert "stability" in result
        assert "impulse_response" in result
        assert "frequency_response" in result
        
        # 检查模型信息
        assert result["model"]["model_type"] == "ARIMA"
        assert result["model"]["parameters"]["p"] == 1
        assert result["model"]["parameters"]["d"] == 0
        assert result["model"]["parameters"]["q"] == 1
        
        # 检查传递函数信息
        assert "numerator" in result["transfer_function"]
        assert "denominator" in result["transfer_function"]
        assert "poles" in result["transfer_function"]
        assert "zeros" in result["transfer_function"]


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_analyze_arima(self):
        """测试ARIMA分析便捷函数"""
        result = analyze_arima(
            p=1, d=0, q=1,
            ar_params=[0.5],
            ma_params=[0.2],
            include_stability=True
        )
        
        assert "model" in result
        assert "transfer_function" in result
        assert "stability" in result
        
        assert result["model"]["model_type"] == "ARIMA"
        assert result["model"]["parameters"]["p"] == 1
    
    def test_analyze_sarima(self):
        """测试SARIMA分析便捷函数"""
        result = analyze_sarima(
            p=1, d=1, q=1,
            P=1, D=1, Q=1, m=12,
            ar_params=[0.5],
            ma_params=[0.2],
            seasonal_ar_params=[0.8],
            seasonal_ma_params=[0.4],
            include_stability=True
        )
        
        assert "model" in result
        assert "transfer_function" in result
        assert "stability" in result
        
        assert result["model"]["model_type"] == "SARIMA"
        assert result["model"]["parameters"]["p"] == 1
        assert result["model"]["seasonal_parameters"]["P"] == 1
        assert result["model"]["seasonal_parameters"]["m"] == 12
    
    def test_parse_and_analyze(self):
        """测试解析并分析便捷函数"""
        result = parse_and_analyze(
            "ARIMA(2,1,1)",
            include_stability=True,
            include_impulse=False,
            include_frequency=False
        )
        
        assert "model" in result
        assert "transfer_function" in result
        assert "stability" in result
        assert "impulse_response" not in result
        assert "frequency_response" not in result
        
        assert result["model"]["parameters"]["p"] == 2
        assert result["model"]["parameters"]["d"] == 1
        assert result["model"]["parameters"]["q"] == 1
    
    def test_parse_and_analyze_sarima(self):
        """测试解析SARIMA并分析"""
        result = parse_and_analyze(
            "SARIMA(1,1,1)(1,1,1,12)",
            include_stability=True
        )
        
        assert "model" in result
        assert result["model"]["model_type"] == "SARIMA"
        assert result["model"]["seasonal_parameters"]["m"] == 12
