"""
测试解析器
"""

import pytest
import json
import yaml
from pathlib import Path
import tempfile
import sys

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from time_series_analyzer.parsers import ModelParser
from time_series_analyzer.models import ARIMAModel, SeasonalARIMAModel


class TestModelParser:
    """测试模型解析器"""
    
    def test_parse_arima_string_basic(self):
        """测试基本ARIMA字符串解析"""
        result = ModelParser.parse_arima_string("ARIMA(2,1,1)")
        
        assert result["model_type"] == "ARIMA"
        assert result["p"] == 2
        assert result["d"] == 1
        assert result["q"] == 1
    
    def test_parse_arima_string_with_params(self):
        """测试带参数的ARIMA字符串解析"""
        result = ModelParser.parse_arima_string("ARIMA(2,1,1,0.5,-0.3,0.2,0.1)")
        
        assert result["model_type"] == "ARIMA"
        assert result["p"] == 2
        assert result["d"] == 1
        assert result["q"] == 1
        assert result["ar_params"] == [0.5, -0.3]
        assert result["ma_params"] == [0.2]
        assert result["constant"] == 0.1
    
    def test_parse_sarima_string(self):
        """测试SARIMA字符串解析"""
        result = ModelParser.parse_arima_string("SARIMA(2,1,1)(1,1,1,12)")
        
        assert result["model_type"] == "SARIMA"
        assert result["p"] == 2
        assert result["d"] == 1
        assert result["q"] == 1
        assert result["P"] == 1
        assert result["D"] == 1
        assert result["Q"] == 1
        assert result["m"] == 12
    
    def test_parse_invalid_string(self):
        """测试无效字符串解析"""
        with pytest.raises(ValueError):
            ModelParser.parse_arima_string("INVALID(2,1,1)")
        
        with pytest.raises(ValueError):
            ModelParser.parse_arima_string("ARIMA(a,b,c)")
    
    def test_parse_json_file(self):
        """测试JSON文件解析"""
        # 创建临时JSON文件
        test_data = {
            "model_type": "ARIMA",
            "p": 2,
            "d": 1,
            "q": 1,
            "ar_params": [0.5, -0.3],
            "ma_params": [0.2],
            "constant": 0.1
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = ModelParser.parse_json_file(temp_path)
            
            assert result["model_type"] == "ARIMA"
            assert result["p"] == 2
            assert result["d"] == 1
            assert result["q"] == 1
            assert result["ar_params"] == [0.5, -0.3]
            assert result["ma_params"] == [0.2]
            assert result["constant"] == 0.1
        finally:
            Path(temp_path).unlink()
    
    def test_parse_yaml_file(self):
        """测试YAML文件解析"""
        # 创建临时YAML文件
        test_data = {
            "model_type": "SARIMA",
            "p": 2,
            "d": 1,
            "q": 1,
            "P": 1,
            "D": 1,
            "Q": 1,
            "m": 12,
            "ar_params": [0.5, -0.3],
            "ma_params": [0.2],
            "seasonal_ar_params": [0.8],
            "seasonal_ma_params": [0.4]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = ModelParser.parse_yaml_file(temp_path)
            
            assert result["model_type"] == "SARIMA"
            assert result["p"] == 2
            assert result["P"] == 1
            assert result["m"] == 12
        finally:
            Path(temp_path).unlink()
    
    def test_create_model_from_dict_arima(self):
        """测试从字典创建ARIMA模型"""
        data = {
            "model_type": "ARIMA",
            "p": 2,
            "d": 1,
            "q": 1,
            "ar_params": [0.5, -0.3],
            "ma_params": [0.2]
        }
        
        model = ModelParser.create_model_from_dict(data)
        
        assert isinstance(model, ARIMAModel)
        assert model.p == 2
        assert model.d == 1
        assert model.q == 1
        assert model.ar_params == [0.5, -0.3]
        assert model.ma_params == [0.2]
    
    def test_create_model_from_dict_sarima(self):
        """测试从字典创建SARIMA模型"""
        data = {
            "model_type": "SARIMA",
            "p": 2,
            "d": 1,
            "q": 1,
            "P": 1,
            "D": 1,
            "Q": 1,
            "m": 12,
            "ar_params": [0.5, -0.3],
            "ma_params": [0.2],
            "seasonal_ar_params": [0.8],
            "seasonal_ma_params": [0.4]
        }
        
        model = ModelParser.create_model_from_dict(data)
        
        assert isinstance(model, SeasonalARIMAModel)
        assert model.p == 2
        assert model.P == 1
        assert model.m == 12
        assert model.seasonal_ar_params == [0.8]
    
    def test_parse_from_string(self):
        """测试从字符串解析并创建模型"""
        model = ModelParser.parse_from_string("ARIMA(2,1,1)")
        
        assert isinstance(model, ARIMAModel)
        assert model.p == 2
        assert model.d == 1
        assert model.q == 1
        assert model.name == "ARIMA(2,1,1)"
    
    def test_validate_config_data(self):
        """测试配置数据验证"""
        # 测试缺少必需字段
        with pytest.raises(ValueError):
            ModelParser._validate_config_data({"model_type": "ARIMA", "p": 2})
        
        # 测试不支持的模型类型
        with pytest.raises(ValueError):
            ModelParser._validate_config_data({
                "model_type": "INVALID",
                "p": 2, "d": 1, "q": 1
            })
        
        # 测试SARIMA缺少季节性字段
        with pytest.raises(ValueError):
            ModelParser._validate_config_data({
                "model_type": "SARIMA",
                "p": 2, "d": 1, "q": 1
                # 缺少P, D, Q, m
            })
    
    def test_file_not_found(self):
        """测试文件不存在的情况"""
        with pytest.raises(FileNotFoundError):
            ModelParser.parse_json_file("nonexistent.json")
        
        with pytest.raises(FileNotFoundError):
            ModelParser.parse_yaml_file("nonexistent.yaml")
    
    def test_unsupported_file_format(self):
        """测试不支持的文件格式"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                ModelParser.parse_from_file(temp_path)
        finally:
            Path(temp_path).unlink()
