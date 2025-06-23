#!/usr/bin/env python3
"""
时序模型传递函数分析器使用示例

演示如何使用Python API进行各种分析任务。
"""

import sys
from pathlib import Path

# 添加src目录到Python路径（仅用于示例）
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from time_series_analyzer import (
    TimeSeriesAnalyzer,
    analyze_arima,
    analyze_sarima,
    parse_and_analyze
)


def example_1_basic_arima():
    """示例1: 基本ARIMA模型分析"""
    print("=" * 60)
    print("示例1: 基本ARIMA模型分析")
    print("=" * 60)
    
    # 创建分析器
    analyzer = TimeSeriesAnalyzer()
    
    # 创建ARIMA(2,1,1)模型
    model = analyzer.create_arima_model(
        p=2, d=1, q=1,
        ar_params=[0.5, -0.3],
        ma_params=[0.2]
    )
    
    print(f"模型: {model}")
    
    # 推导传递函数
    transfer_func = analyzer.derive_transfer_function(model)
    print(f"传递函数: {transfer_func}")
    
    # 分析稳定性
    stability = analyzer.analyze_stability(model)
    print(f"系统稳定性: {'稳定' if stability['is_stable'] else '不稳定'}")
    print(f"最大极点模长: {stability['max_pole_magnitude']:.4f}")
    
    print()


def example_2_sarima_model():
    """示例2: SARIMA模型分析"""
    print("=" * 60)
    print("示例2: SARIMA模型分析")
    print("=" * 60)
    
    analyzer = TimeSeriesAnalyzer()
    
    # 创建SARIMA(1,1,1)(1,1,1,12)模型
    model = analyzer.create_sarima_model(
        p=1, d=1, q=1,
        P=1, D=1, Q=1, m=12,
        ar_params=[0.7],
        ma_params=[0.3],
        seasonal_ar_params=[0.5],
        seasonal_ma_params=[0.2]
    )
    
    print(f"模型: {model}")
    
    # 推导传递函数
    transfer_func = analyzer.derive_transfer_function(model)
    print(f"传递函数: {transfer_func}")
    
    # 计算脉冲响应
    impulse_response = analyzer.compute_impulse_response(model, max_lag=5)
    print("脉冲响应:")
    for lag, coeff in impulse_response.items():
        print(f"  h[{lag}] = {coeff}")
    
    print()


def example_3_convenience_functions():
    """示例3: 使用便捷函数"""
    print("=" * 60)
    print("示例3: 使用便捷函数")
    print("=" * 60)
    
    # 快速分析ARIMA模型
    result = analyze_arima(
        p=1, d=0, q=1,
        ar_params=[0.8],
        ma_params=[0.4],
        include_stability=True,
        include_impulse=True,
        max_lag=5
    )
    
    print("ARIMA(1,0,1)分析结果:")
    print(f"  传递函数分子: {result['transfer_function']['numerator']}")
    print(f"  传递函数分母: {result['transfer_function']['denominator']}")
    print(f"  稳定性: {'稳定' if result['stability']['is_stable'] else '不稳定'}")
    
    # 从字符串解析并分析
    result2 = parse_and_analyze(
        "ARIMA(2,1,2)",
        include_stability=True
    )
    
    print(f"\nARIMA(2,1,2)稳定性: {'稳定' if result2['stability']['is_stable'] else '不稳定'}")
    
    print()


def example_4_frequency_response():
    """示例4: 频率响应分析"""
    print("=" * 60)
    print("示例4: 频率响应分析")
    print("=" * 60)
    
    analyzer = TimeSeriesAnalyzer()
    
    # 创建简单的AR(1)模型
    model = analyzer.create_arima_model(
        p=1, d=0, q=0,
        ar_params=[0.8]
    )
    
    # 计算频率响应
    frequencies = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
    freq_response = analyzer.compute_frequency_response(model, frequencies)
    
    print("AR(1)模型频率响应:")
    print(f"{'频率':<8} {'幅度':<12} {'相位':<12} {'幅度(dB)':<12}")
    print("-" * 50)
    
    for i, freq in enumerate(freq_response["frequencies"]):
        mag = float(freq_response["magnitudes"][i])
        phase = float(freq_response["phases"][i])
        mag_db = float(freq_response["magnitude_db"][i])
        print(f"{freq:<8.2f} {mag:<12.4f} {phase:<12.4f} {mag_db:<12.2f}")
    
    print()


def example_5_report_generation():
    """示例5: 生成分析报告"""
    print("=" * 60)
    print("示例5: 生成分析报告")
    print("=" * 60)
    
    analyzer = TimeSeriesAnalyzer()
    
    # 创建模型
    model = analyzer.create_arima_model(
        p=2, d=1, q=1,
        ar_params=[0.6, -0.2],
        ma_params=[0.3]
    )
    
    # 生成文本报告
    report = analyzer.generate_report(
        model,
        format='text',
        include_analysis=True
    )
    
    print("文本格式报告:")
    print(report)


def example_6_symbolic_parameters():
    """示例6: 符号参数模型"""
    print("=" * 60)
    print("示例6: 符号参数模型")
    print("=" * 60)
    
    analyzer = TimeSeriesAnalyzer()
    
    # 创建带符号参数的模型
    model = analyzer.create_arima_model(
        p=2, d=1, q=1
        # 不提供具体参数值，将使用符号参数
    )
    
    print(f"模型: {model}")
    print(f"AR参数: {model.ar_params}")
    print(f"MA参数: {model.ma_params}")
    
    # 推导传递函数
    transfer_func = analyzer.derive_transfer_function(model)
    print(f"符号传递函数: {transfer_func}")
    
    print()


def example_7_model_comparison():
    """示例7: 模型比较"""
    print("=" * 60)
    print("示例7: 模型比较")
    print("=" * 60)
    
    analyzer = TimeSeriesAnalyzer()
    
    # 比较不同的AR(1)模型
    ar_params = [0.3, 0.6, 0.9]
    
    print("AR(1)模型稳定性比较:")
    print(f"{'AR参数':<10} {'稳定性':<10} {'极点模长':<12}")
    print("-" * 35)
    
    for param in ar_params:
        model = analyzer.create_arima_model(p=1, d=0, q=0, ar_params=[param])
        stability = analyzer.analyze_stability(model)
        
        is_stable = "稳定" if stability["is_stable"] else "不稳定"
        max_mag = stability["max_pole_magnitude"]
        
        print(f"{param:<10.1f} {is_stable:<10} {max_mag:<12.4f}")
    
    print()


def main():
    """运行所有示例"""
    print("时序模型传递函数分析器 - 使用示例")
    print("=" * 60)
    print()
    
    try:
        example_1_basic_arima()
        example_2_sarima_model()
        example_3_convenience_functions()
        example_4_frequency_response()
        example_5_report_generation()
        example_6_symbolic_parameters()
        example_7_model_comparison()
        
        print("所有示例运行完成！")
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
