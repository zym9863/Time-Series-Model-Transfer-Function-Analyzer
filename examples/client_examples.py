#!/usr/bin/env python3
"""
API客户端使用示例

演示如何使用Python客户端库调用时间序列分析API
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.client import create_client
import json

def print_result(result, title: str):
    """格式化打印结果"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(json.dumps(result, indent=2, ensure_ascii=False))

def main():
    """主函数"""
    # 创建客户端
    client = create_client("http://localhost:8000")
    
    try:
        # 1. 健康检查
        health = client.health_check()
        print_result(health, "1. 健康检查")
        
        # 2. 获取支持的模型
        models = client.get_supported_models()
        print_result(models, "2. 支持的模型类型")
        
        # 3. 分析ARIMA模型
        arima_result = client.analyze_arima(
            p=2, d=1, q=1,
            ar_params=[0.5, -0.3],
            ma_params=[0.2],
            name="客户端测试ARIMA模型",
            include_stability=True,
            include_impulse=True,
            max_lag=10
        )
        print_result(arima_result, "3. ARIMA模型分析")
        
        # 4. 分析SARIMA模型
        sarima_result = client.analyze_sarima(
            p=1, d=1, q=1,
            P=1, D=1, Q=1, m=12,
            ar_params=[0.7],
            ma_params=[0.3],
            seasonal_ar_params=[0.5],
            seasonal_ma_params=[0.2],
            name="客户端测试SARIMA模型",
            include_stability=True,
            include_frequency=True,
            frequencies=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
        )
        print_result(sarima_result, "4. SARIMA模型分析")
        
        # 5. 通过模型字符串分析
        string_result = client.analyze_model_string(
            model_string="ARIMA(2,1,1)",
            include_stability=True,
            include_impulse=True,
            max_lag=15
        )
        print_result(string_result, "5. 模型字符串分析")
        
        # 6. 仅获取传递函数
        tf_result = client.get_transfer_function("ARIMA(1,1,1)")
        print_result(tf_result, "6. 传递函数推导")
        
        # 7. 仅获取稳定性分析
        stability_result = client.get_stability_analysis("ARIMA(1,1,1)")
        print_result(stability_result, "7. 稳定性分析")
        
        # 8. 验证模型字符串
        validation_result = client.validate_model_string("ARIMA(2,1,1)")
        print_result(validation_result, "8. 模型字符串验证")
        
        print(f"\n{'='*50}")
        print("所有客户端示例执行完成！")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"执行过程中发生错误：{e}")
        print("请确保API服务已启动：python scripts/start_api.py")

if __name__ == "__main__":
    main()
