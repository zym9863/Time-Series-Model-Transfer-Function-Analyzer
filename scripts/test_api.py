#!/usr/bin/env python3
"""
FastAPI服务功能测试脚本

验证所有API端点是否正常工作
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.client import create_client

def test_api_endpoints():
    """测试所有API端点"""
    
    print("🚀 开始测试FastAPI服务...")
    
    try:
        # 创建客户端
        client = create_client("http://localhost:8000")
        
        # 测试计数器
        tests_passed = 0
        tests_total = 0
        
        # 1. 健康检查
        print("\n1️⃣ 测试健康检查...")
        tests_total += 1
        try:
            health = client.health_check()
            assert health["status"] == "healthy"
            print("✅ 健康检查通过")
            tests_passed += 1
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
        
        # 2. 获取支持的模型
        print("\n2️⃣ 测试模型类型获取...")
        tests_total += 1
        try:
            models = client.get_supported_models()
            assert "ARIMA" in models["models"]
            assert "SARIMA" in models["models"]
            print("✅ 模型类型获取通过")
            tests_passed += 1
        except Exception as e:
            print(f"❌ 模型类型获取失败: {e}")
        
        # 3. ARIMA模型分析
        print("\n3️⃣ 测试ARIMA模型分析...")
        tests_total += 1
        try:
            result = client.analyze_arima(
                p=2, d=1, q=1,
                ar_params=[0.5, -0.3],
                ma_params=[0.2],
                include_stability=True,
                include_impulse=True,
                max_lag=5
            )
            assert result["model"]["model_type"] == "ARIMA"
            assert "transfer_function" in result
            assert "stability" in result
            assert "impulse_response" in result
            print("✅ ARIMA模型分析通过")
            tests_passed += 1
        except Exception as e:
            print(f"❌ ARIMA模型分析失败: {e}")
        
        # 4. SARIMA模型分析
        print("\n4️⃣ 测试SARIMA模型分析...")
        tests_total += 1
        try:
            result = client.analyze_sarima(
                p=1, d=1, q=1,
                P=1, D=1, Q=1, m=12,
                ar_params=[0.7],
                ma_params=[0.3],
                seasonal_ar_params=[0.5],
                seasonal_ma_params=[0.2],
                include_stability=True,
                include_frequency=True,
                frequencies=[0.0, 0.1, 0.2]
            )
            assert result["model"]["model_type"] == "SARIMA"
            assert "transfer_function" in result
            assert "stability" in result
            assert "frequency_response" in result
            print("✅ SARIMA模型分析通过")
            tests_passed += 1
        except Exception as e:
            print(f"❌ SARIMA模型分析失败: {e}")
        
        # 5. 模型字符串分析
        print("\n5️⃣ 测试模型字符串分析...")
        tests_total += 1
        try:
            result = client.analyze_model_string(
                model_string="ARIMA(1,1,1)",
                include_stability=True
            )
            assert result["model"]["model_type"] == "ARIMA"
            assert "transfer_function" in result
            print("✅ 模型字符串分析通过")
            tests_passed += 1
        except Exception as e:
            print(f"❌ 模型字符串分析失败: {e}")
        
        # 6. 传递函数推导
        print("\n6️⃣ 测试传递函数推导...")
        tests_total += 1
        try:
            result = client.get_transfer_function("ARIMA(1,1,1)")
            assert "transfer_function" in result
            assert "numerator" in result["transfer_function"]
            assert "denominator" in result["transfer_function"]
            print("✅ 传递函数推导通过")
            tests_passed += 1
        except Exception as e:
            print(f"❌ 传递函数推导失败: {e}")
        
        # 7. 稳定性分析
        print("\n7️⃣ 测试稳定性分析...")
        tests_total += 1
        try:
            result = client.get_stability_analysis("ARIMA(1,1,1)")
            assert "stability" in result
            assert "is_stable" in result["stability"]
            print("✅ 稳定性分析通过")
            tests_passed += 1
        except Exception as e:
            print(f"❌ 稳定性分析失败: {e}")
        
        # 8. 模型字符串验证
        print("\n8️⃣ 测试模型字符串验证...")
        tests_total += 1
        try:
            result = client.validate_model_string("ARIMA(2,1,1)")
            assert result["valid"] == True
            print("✅ 模型字符串验证通过")
            tests_passed += 1
        except Exception as e:
            print(f"❌ 模型字符串验证失败: {e}")
        
        # 测试结果总结
        print(f"\n{'='*50}")
        print(f"📊 测试结果总结")
        print(f"{'='*50}")
        print(f"✅ 通过: {tests_passed}/{tests_total}")
        print(f"❌ 失败: {tests_total - tests_passed}/{tests_total}")
        print(f"📈 成功率: {tests_passed/tests_total*100:.1f}%")
        
        if tests_passed == tests_total:
            print(f"\n🎉 所有测试通过！FastAPI服务运行正常。")
            return True
        else:
            print(f"\n⚠️  有 {tests_total - tests_passed} 个测试失败，请检查服务状态。")
            return False
            
    except Exception as e:
        print(f"\n💥 测试过程中发生严重错误: {e}")
        print("请确保FastAPI服务已启动：python scripts/start_api.py")
        return False

def main():
    """主函数"""
    print("时间序列模型传递函数分析器 - FastAPI服务测试")
    print("=" * 60)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)
    
    # 运行测试
    success = test_api_endpoints()
    
    # 退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
