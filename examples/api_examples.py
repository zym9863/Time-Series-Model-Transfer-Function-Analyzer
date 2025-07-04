#!/usr/bin/env python3
"""
FastAPI服务使用示例

演示如何通过HTTP API调用时间序列模型分析服务
"""

import requests
import json
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def check_health() -> Dict[str, Any]:
    """检查服务健康状态"""
    response = requests.get(f"{BASE_URL}/health")
    return response.json()

def get_supported_models() -> Dict[str, Any]:
    """获取支持的模型类型"""
    response = requests.get(f"{BASE_URL}/models")
    return response.json()

def analyze_arima_model() -> Dict[str, Any]:
    """分析ARIMA模型示例"""
    data = {
        "p": 2,
        "d": 1,
        "q": 1,
        "ar_params": [0.5, -0.3],
        "ma_params": [0.2],
        "constant": 0.0,
        "name": "示例ARIMA(2,1,1)模型",
        "include_stability": True,
        "include_impulse": True,
        "include_frequency": False,
        "max_lag": 10
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze/arima",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    return response.json()

def analyze_sarima_model() -> Dict[str, Any]:
    """分析SARIMA模型示例"""
    data = {
        "p": 1, "d": 1, "q": 1,
        "P": 1, "D": 1, "Q": 1, "m": 12,
        "ar_params": [0.7],
        "ma_params": [0.3],
        "seasonal_ar_params": [0.5],
        "seasonal_ma_params": [0.2],
        "name": "示例SARIMA(1,1,1)(1,1,1,12)模型",
        "include_stability": True,
        "include_impulse": False,
        "include_frequency": True,
        "frequencies": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze/sarima",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    return response.json()

def analyze_model_string() -> Dict[str, Any]:
    """通过模型字符串分析"""
    data = {
        "model_string": "ARIMA(2,1,1)",
        "include_stability": True,
        "include_impulse": True,
        "max_lag": 15
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze/model-string",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    return response.json()

def get_transfer_function(model_string: str) -> Dict[str, Any]:
    """仅获取传递函数"""
    response = requests.get(f"{BASE_URL}/analyze/transfer-function/{model_string}")
    return response.json()

def get_stability_analysis(model_string: str) -> Dict[str, Any]:
    """仅获取稳定性分析"""
    response = requests.get(f"{BASE_URL}/analyze/stability/{model_string}")
    return response.json()

def print_json(data: Dict[str, Any], title: str):
    """格式化打印JSON数据"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    """主函数 - 运行所有示例"""
    try:
        # 1. 健康检查
        health = check_health()
        print_json(health, "1. 健康检查")
        
        # 2. 获取支持的模型
        models = get_supported_models()
        print_json(models, "2. 支持的模型类型")
        
        # 3. ARIMA模型分析
        arima_result = analyze_arima_model()
        print_json(arima_result, "3. ARIMA模型分析")
        
        # 4. SARIMA模型分析
        sarima_result = analyze_sarima_model()
        print_json(sarima_result, "4. SARIMA模型分析")
        
        # 5. 模型字符串分析
        string_result = analyze_model_string()
        print_json(string_result, "5. 模型字符串分析")
        
        # 6. 仅获取传递函数
        tf_result = get_transfer_function("ARIMA(1,1,1)")
        print_json(tf_result, "6. 传递函数推导")
        
        # 7. 仅获取稳定性分析
        stability_result = get_stability_analysis("ARIMA(1,1,1)")
        print_json(stability_result, "7. 稳定性分析")
        
        print(f"\n{'='*50}")
        print("所有API示例执行完成！")
        print(f"{'='*50}")
        
    except requests.exceptions.ConnectionError:
        print("错误：无法连接到API服务")
        print("请确保服务已启动：python scripts/start_api.py")
    except Exception as e:
        print(f"执行过程中发生错误：{e}")

if __name__ == "__main__":
    main()
