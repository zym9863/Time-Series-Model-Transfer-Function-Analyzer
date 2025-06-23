"""
模型参数解析模块

支持多种输入方式：命令行参数、配置文件（JSON/YAML）、交互式输入等。
"""

import json
import yaml
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import re

from .models import ARIMAModel, SeasonalARIMAModel


class ModelParser:
    """模型参数解析器"""
    
    @staticmethod
    def parse_arima_string(arima_str: str) -> Dict[str, Any]:
        """
        解析ARIMA字符串格式
        
        支持格式:
        - "ARIMA(2,1,1)"
        - "ARIMA(2,1,1,0.5,-0.3,0.2)"  # 包含参数
        - "SARIMA(2,1,1)(1,1,1,12)"
        
        Args:
            arima_str: ARIMA模型字符串
            
        Returns:
            解析后的参数字典
        """
        arima_str = arima_str.strip().upper()
        
        # 匹配SARIMA格式
        sarima_pattern = r'SARIMA\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
        sarima_match = re.match(sarima_pattern, arima_str)
        
        if sarima_match:
            p, d, q, P, D, Q, m = map(int, sarima_match.groups())
            return {
                "model_type": "SARIMA",
                "p": p, "d": d, "q": q,
                "P": P, "D": D, "Q": Q, "m": m
            }
        
        # 匹配ARIMA格式
        arima_pattern = r'ARIMA\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*(.*))?\s*\)'
        arima_match = re.match(arima_pattern, arima_str)
        
        if arima_match:
            p, d, q = map(int, arima_match.groups()[:3])
            params_str = arima_match.group(4)
            
            result = {
                "model_type": "ARIMA",
                "p": p, "d": d, "q": q
            }
            
            # 解析参数
            if params_str:
                try:
                    params = [float(x.strip()) for x in params_str.split(',')]
                    if len(params) >= p:
                        result["ar_params"] = params[:p]
                    if len(params) >= p + q:
                        result["ma_params"] = params[p:p+q]
                    if len(params) > p + q:
                        result["constant"] = params[p+q]
                except ValueError:
                    pass  # 忽略参数解析错误
            
            return result
        
        raise ValueError(f"无法解析ARIMA字符串: {arima_str}")
    
    @staticmethod
    def parse_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        从JSON文件解析模型参数
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            解析后的参数字典
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return ModelParser._validate_config_data(data)
    
    @staticmethod
    def parse_yaml_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        从YAML文件解析模型参数
        
        Args:
            file_path: YAML文件路径
            
        Returns:
            解析后的参数字典
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return ModelParser._validate_config_data(data)
    
    @staticmethod
    def _validate_config_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证配置数据格式"""
        required_fields = ["model_type", "p", "d", "q"]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"配置文件缺少必需字段: {field}")
        
        model_type = data["model_type"].upper()
        if model_type not in ["ARIMA", "SARIMA"]:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        if model_type == "SARIMA":
            seasonal_fields = ["P", "D", "Q", "m"]
            for field in seasonal_fields:
                if field not in data:
                    raise ValueError(f"SARIMA模型缺少必需字段: {field}")
        
        return data
    
    @staticmethod
    def interactive_input() -> Dict[str, Any]:
        """
        交互式输入模型参数
        
        Returns:
            解析后的参数字典
        """
        print("=== 时序模型参数输入 ===")
        
        # 选择模型类型
        while True:
            model_type = input("请选择模型类型 (1: ARIMA, 2: SARIMA): ").strip()
            if model_type in ["1", "ARIMA", "arima"]:
                model_type = "ARIMA"
                break
            elif model_type in ["2", "SARIMA", "sarima"]:
                model_type = "SARIMA"
                break
            else:
                print("无效输入，请重新选择")
        
        # 输入基本参数
        try:
            p = int(input("请输入自回归阶数 p: "))
            d = int(input("请输入差分阶数 d: "))
            q = int(input("请输入移动平均阶数 q: "))
        except ValueError:
            raise ValueError("参数必须是非负整数")
        
        result = {
            "model_type": model_type,
            "p": p, "d": d, "q": q
        }
        
        # 输入季节性参数
        if model_type == "SARIMA":
            try:
                P = int(input("请输入季节性自回归阶数 P: "))
                D = int(input("请输入季节性差分阶数 D: "))
                Q = int(input("请输入季节性移动平均阶数 Q: "))
                m = int(input("请输入季节性周期 m: "))
            except ValueError:
                raise ValueError("季节性参数必须是非负整数")
            
            result.update({"P": P, "D": D, "Q": Q, "m": m})
        
        # 询问是否输入具体参数值
        if input("是否输入具体参数值? (y/n): ").lower().startswith('y'):
            if p > 0:
                ar_params = []
                for i in range(p):
                    try:
                        param = float(input(f"请输入AR参数 φ_{i+1}: "))
                        ar_params.append(param)
                    except ValueError:
                        print(f"使用符号参数 phi_{i+1}")
                        ar_params.append(f"phi_{i+1}")
                result["ar_params"] = ar_params
            
            if q > 0:
                ma_params = []
                for i in range(q):
                    try:
                        param = float(input(f"请输入MA参数 θ_{i+1}: "))
                        ma_params.append(param)
                    except ValueError:
                        print(f"使用符号参数 theta_{i+1}")
                        ma_params.append(f"theta_{i+1}")
                result["ma_params"] = ma_params
            
            if model_type == "SARIMA":
                if result.get("P", 0) > 0:
                    seasonal_ar_params = []
                    for i in range(result["P"]):
                        try:
                            param = float(input(f"请输入季节性AR参数 Φ_{i+1}: "))
                            seasonal_ar_params.append(param)
                        except ValueError:
                            print(f"使用符号参数 Phi_{i+1}")
                            seasonal_ar_params.append(f"Phi_{i+1}")
                    result["seasonal_ar_params"] = seasonal_ar_params
                
                if result.get("Q", 0) > 0:
                    seasonal_ma_params = []
                    for i in range(result["Q"]):
                        try:
                            param = float(input(f"请输入季节性MA参数 Θ_{i+1}: "))
                            seasonal_ma_params.append(param)
                        except ValueError:
                            print(f"使用符号参数 Theta_{i+1}")
                            seasonal_ma_params.append(f"Theta_{i+1}")
                    result["seasonal_ma_params"] = seasonal_ma_params
            
            # 常数项
            try:
                constant = float(input("请输入常数项 (默认0): ") or "0")
                result["constant"] = constant
            except ValueError:
                result["constant"] = 0
        
        return result
    
    @staticmethod
    def create_model_from_dict(data: Dict[str, Any]) -> Union[ARIMAModel, SeasonalARIMAModel]:
        """
        从字典创建模型对象
        
        Args:
            data: 参数字典
            
        Returns:
            模型对象
        """
        model_type = data.get("model_type", "ARIMA").upper()
        
        if model_type == "SARIMA":
            # 移除model_type字段
            sarima_data = {k: v for k, v in data.items() if k != "model_type"}
            return SeasonalARIMAModel(**sarima_data)
        else:
            # 移除SARIMA特有的字段和model_type字段
            arima_data = {k: v for k, v in data.items()
                         if k not in ["model_type", "P", "D", "Q", "m", "seasonal_ar_params", "seasonal_ma_params"]}
            return ARIMAModel(**arima_data)
    
    @staticmethod
    def parse_from_string(input_str: str) -> Union[ARIMAModel, SeasonalARIMAModel]:
        """
        从字符串解析并创建模型
        
        Args:
            input_str: 输入字符串
            
        Returns:
            模型对象
        """
        data = ModelParser.parse_arima_string(input_str)
        return ModelParser.create_model_from_dict(data)
    
    @staticmethod
    def parse_from_file(file_path: Union[str, Path]) -> Union[ARIMAModel, SeasonalARIMAModel]:
        """
        从文件解析并创建模型
        
        Args:
            file_path: 文件路径
            
        Returns:
            模型对象
        """
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.json':
            data = ModelParser.parse_json_file(file_path)
        elif file_path.suffix.lower() in ['.yaml', '.yml']:
            data = ModelParser.parse_yaml_file(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")
        
        return ModelParser.create_model_from_dict(data)
    
    @staticmethod
    def parse_interactive() -> Union[ARIMAModel, SeasonalARIMAModel]:
        """
        交互式解析并创建模型
        
        Returns:
            模型对象
        """
        data = ModelParser.interactive_input()
        return ModelParser.create_model_from_dict(data)
