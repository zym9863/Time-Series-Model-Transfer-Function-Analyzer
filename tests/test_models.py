"""
测试模型类
"""

import pytest
from sympy import symbols
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from time_series_analyzer.models import ARIMAModel, SeasonalARIMAModel


class TestARIMAModel:
    """测试ARIMA模型类"""
    
    def test_basic_arima_creation(self):
        """测试基本ARIMA模型创建"""
        model = ARIMAModel(p=2, d=1, q=1)
        assert model.p == 2
        assert model.d == 1
        assert model.q == 1
        assert model.name == "ARIMA(2,1,1)"
    
    def test_arima_with_params(self):
        """测试带参数的ARIMA模型"""
        ar_params = [0.5, -0.3]
        ma_params = [0.2]
        
        model = ARIMAModel(
            p=2, d=1, q=1,
            ar_params=ar_params,
            ma_params=ma_params,
            constant=0.1
        )
        
        assert model.ar_params == ar_params
        assert model.ma_params == ma_params
        assert model.constant == 0.1
    
    def test_arima_validation(self):
        """测试ARIMA模型验证"""
        # 测试参数长度不匹配
        with pytest.raises(ValueError):
            ARIMAModel(p=2, d=1, q=1, ar_params=[0.5])  # 长度不匹配
        
        with pytest.raises(ValueError):
            ARIMAModel(p=2, d=1, q=1, ma_params=[0.2, 0.3])  # 长度不匹配
        
        # 测试全零参数
        with pytest.raises(ValueError):
            ARIMAModel(p=0, d=0, q=0)
    
    def test_ar_polynomial(self):
        """测试自回归多项式"""
        model = ARIMAModel(p=2, d=0, q=0, ar_params=[0.5, -0.3])
        B = symbols('B')
        ar_poly = model.get_ar_polynomial(B)
        
        # φ(B) = 1 - 0.5B + 0.3B²
        expected_coeffs = [1, -0.5, 0.3]
        actual_coeffs = ar_poly.all_coeffs()
        
        assert len(actual_coeffs) == len(expected_coeffs)
        for actual, expected in zip(actual_coeffs, expected_coeffs):
            assert abs(float(actual) - expected) < 1e-10
    
    def test_ma_polynomial(self):
        """测试移动平均多项式"""
        model = ARIMAModel(p=0, d=0, q=2, ma_params=[0.2, 0.4])
        B = symbols('B')
        ma_poly = model.get_ma_polynomial(B)
        
        # θ(B) = 1 + 0.2B + 0.4B²
        expected_coeffs = [1, 0.2, 0.4]
        actual_coeffs = ma_poly.all_coeffs()
        
        assert len(actual_coeffs) == len(expected_coeffs)
        for actual, expected in zip(actual_coeffs, expected_coeffs):
            assert abs(float(actual) - expected) < 1e-10
    
    def test_difference_polynomial(self):
        """测试差分多项式"""
        model = ARIMAModel(p=0, d=2, q=0)
        B = symbols('B')
        diff_poly = model.get_difference_polynomial(B)
        
        # (1-B)² = 1 - 2B + B²
        expected_coeffs = [1, -2, 1]
        actual_coeffs = diff_poly.all_coeffs()
        
        assert len(actual_coeffs) == len(expected_coeffs)
        for actual, expected in zip(actual_coeffs, expected_coeffs):
            assert abs(float(actual) - expected) < 1e-10
    
    def test_to_dict(self):
        """测试转换为字典"""
        model = ARIMAModel(
            p=2, d=1, q=1,
            ar_params=[0.5, -0.3],
            ma_params=[0.2],
            constant=0.1
        )
        
        result = model.to_dict()
        
        assert result["model_type"] == "ARIMA"
        assert result["parameters"]["p"] == 2
        assert result["parameters"]["d"] == 1
        assert result["parameters"]["q"] == 1
        assert result["ar_params"] == [0.5, -0.3]
        assert result["ma_params"] == [0.2]
        assert result["constant"] == 0.1


class TestSeasonalARIMAModel:
    """测试季节性ARIMA模型类"""
    
    def test_basic_sarima_creation(self):
        """测试基本SARIMA模型创建"""
        model = SeasonalARIMAModel(
            p=2, d=1, q=1,
            P=1, D=1, Q=1, m=12
        )
        
        assert model.p == 2
        assert model.d == 1
        assert model.q == 1
        assert model.P == 1
        assert model.D == 1
        assert model.Q == 1
        assert model.m == 12
        assert model.name == "SARIMA(2,1,1)(1,1,1,12)"
    
    def test_sarima_with_params(self):
        """测试带参数的SARIMA模型"""
        model = SeasonalARIMAModel(
            p=1, d=1, q=1,
            P=1, D=1, Q=1, m=12,
            ar_params=[0.5],
            ma_params=[0.2],
            seasonal_ar_params=[0.8],
            seasonal_ma_params=[0.4]
        )
        
        assert model.ar_params == [0.5]
        assert model.ma_params == [0.2]
        assert model.seasonal_ar_params == [0.8]
        assert model.seasonal_ma_params == [0.4]
    
    def test_seasonal_ar_polynomial(self):
        """测试季节性自回归多项式"""
        model = SeasonalARIMAModel(
            p=0, d=0, q=0,
            P=1, D=0, Q=0, m=12,
            seasonal_ar_params=[0.8]
        )
        
        B = symbols('B')
        seasonal_ar_poly = model.get_seasonal_ar_polynomial(B)
        
        # Φ(B¹²) = 1 - 0.8B¹²
        # 系数应该是 [1, 0, 0, ..., 0, -0.8] (13个元素)
        coeffs = seasonal_ar_poly.all_coeffs()
        
        assert len(coeffs) == 13  # 0到12次幂
        assert abs(float(coeffs[0]) - 1) < 1e-10  # 常数项
        assert abs(float(coeffs[-1]) - (-0.8)) < 1e-10  # B¹²项
        
        # 中间项应该都是0
        for i in range(1, 12):
            assert abs(float(coeffs[i])) < 1e-10
    
    def test_seasonal_difference_polynomial(self):
        """测试季节性差分多项式"""
        model = SeasonalARIMAModel(
            p=0, d=0, q=0,
            P=0, D=1, Q=0, m=4
        )
        
        B = symbols('B')
        seasonal_diff_poly = model.get_seasonal_difference_polynomial(B)
        
        # (1-B⁴) = 1 - B⁴
        coeffs = seasonal_diff_poly.all_coeffs()
        
        assert len(coeffs) == 5  # 0到4次幂
        assert abs(float(coeffs[0]) - 1) < 1e-10  # 常数项
        assert abs(float(coeffs[-1]) - (-1)) < 1e-10  # B⁴项
        
        # 中间项应该都是0
        for i in range(1, 4):
            assert abs(float(coeffs[i])) < 1e-10
    
    def test_sarima_validation(self):
        """测试SARIMA模型验证"""
        # 测试季节性参数长度不匹配
        with pytest.raises(ValueError):
            SeasonalARIMAModel(
                p=1, d=1, q=1,
                P=2, D=1, Q=1, m=12,
                seasonal_ar_params=[0.8]  # 长度应该是2
            )
    
    def test_sarima_to_dict(self):
        """测试SARIMA转换为字典"""
        model = SeasonalARIMAModel(
            p=1, d=1, q=1,
            P=1, D=1, Q=1, m=12,
            ar_params=[0.5],
            ma_params=[0.2],
            seasonal_ar_params=[0.8],
            seasonal_ma_params=[0.4]
        )
        
        result = model.to_dict()
        
        assert result["model_type"] == "SARIMA"
        assert result["seasonal_parameters"]["P"] == 1
        assert result["seasonal_parameters"]["D"] == 1
        assert result["seasonal_parameters"]["Q"] == 1
        assert result["seasonal_parameters"]["m"] == 12
        assert result["seasonal_ar_params"] == [0.8]
        assert result["seasonal_ma_params"] == [0.4]
