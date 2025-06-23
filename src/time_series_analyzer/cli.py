"""
命令行界面

使用click框架实现用户友好的命令行工具。
"""

import click
from pathlib import Path
from typing import Optional
import sys

from .parsers import ModelParser
from .formatters import OutputFormatter
from .transfer_function import TransferFunctionDeriver
from .models import ARIMAModel, SeasonalARIMAModel


@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    时序模型传递函数分析器
    
    自动推导ARIMA和SARIMA模型的传递函数表达式。
    """
    pass


@main.command()
@click.option('--model', '-m', 
              help='模型字符串，如 "ARIMA(2,1,1)" 或 "SARIMA(2,1,1)(1,1,1,12)"')
@click.option('--file', '-f', type=click.Path(exists=True),
              help='包含模型参数的配置文件 (JSON/YAML)')
@click.option('--interactive', '-i', is_flag=True,
              help='交互式输入模型参数')
@click.option('--output', '-o', type=click.Path(),
              help='输出文件路径')
@click.option('--format', 'output_format', 
              type=click.Choice(['text', 'latex', 'json'], case_sensitive=False),
              default='text', help='输出格式')
@click.option('--include-analysis', is_flag=True,
              help='包含稳定性分析')
@click.option('--precision', type=int, default=4,
              help='数值精度 (小数位数)')
def analyze(model: Optional[str], file: Optional[str], interactive: bool,
           output: Optional[str], output_format: str, include_analysis: bool,
           precision: int):
    """
    分析时间序列模型并生成传递函数
    """
    try:
        # 解析模型
        if interactive:
            model_obj = ModelParser.parse_interactive()
        elif file:
            model_obj = ModelParser.parse_from_file(file)
        elif model:
            model_obj = ModelParser.parse_from_string(model)
        else:
            click.echo("错误: 必须指定模型参数 (使用 --model, --file 或 --interactive)", err=True)
            sys.exit(1)
        
        # 创建格式化器
        formatter = OutputFormatter(precision=precision)
        
        # 生成输出
        if output_format.lower() == 'latex':
            result = formatter.format_latex(
                model_obj, 
                include_transfer_function=True,
                include_analysis=include_analysis
            )
        elif output_format.lower() == 'json':
            result = formatter.format_json(
                model_obj,
                include_transfer_function=True,
                include_analysis=include_analysis
            )
        else:  # text
            result = formatter.format_plain_text(
                model_obj,
                include_transfer_function=True,
                include_analysis=include_analysis
            )
        
        # 输出结果
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            click.echo(f"结果已保存到: {output}")
        else:
            click.echo(result)
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--model', '-m', required=True,
              help='模型字符串，如 "ARIMA(2,1,1)" 或 "SARIMA(2,1,1)(1,1,1,12)"')
@click.option('--max-lag', type=int, default=20,
              help='最大滞后阶数')
@click.option('--output', '-o', type=click.Path(),
              help='输出文件路径')
@click.option('--format', 'output_format',
              type=click.Choice(['text', 'json'], case_sensitive=False),
              default='text', help='输出格式')
def impulse(model: str, max_lag: int, output: Optional[str], output_format: str):
    """
    计算脉冲响应函数
    """
    try:
        # 解析模型
        model_obj = ModelParser.parse_from_string(model)
        
        # 计算脉冲响应
        deriver = TransferFunctionDeriver()
        impulse_response = deriver.derive_impulse_response(model_obj, max_lag)
        
        # 格式化输出
        if output_format.lower() == 'json':
            import json
            result = json.dumps({
                "model": model_obj.to_dict(),
                "impulse_response": {str(k): str(v) for k, v in impulse_response.items()},
                "max_lag": max_lag
            }, indent=2, ensure_ascii=False)
        else:
            lines = [f"{model_obj.name} 脉冲响应函数", "=" * 40]
            for lag, coeff in impulse_response.items():
                lines.append(f"h[{lag}] = {coeff}")
            result = "\n".join(lines)
        
        # 输出结果
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            click.echo(f"脉冲响应已保存到: {output}")
        else:
            click.echo(result)
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--model', '-m', required=True,
              help='模型字符串，如 "ARIMA(2,1,1)" 或 "SARIMA(2,1,1)(1,1,1,12)"')
@click.option('--frequencies', type=str, default="0,0.1,0.2,0.3,0.4,0.5",
              help='频率列表 (逗号分隔)')
@click.option('--output', '-o', type=click.Path(),
              help='输出文件路径')
@click.option('--format', 'output_format',
              type=click.Choice(['text', 'json'], case_sensitive=False),
              default='text', help='输出格式')
def frequency(model: str, frequencies: str, output: Optional[str], output_format: str):
    """
    计算频率响应
    """
    try:
        # 解析模型
        model_obj = ModelParser.parse_from_string(model)
        
        # 解析频率
        freq_list = [float(f.strip()) for f in frequencies.split(',')]
        
        # 计算频率响应
        deriver = TransferFunctionDeriver()
        freq_response = deriver.get_frequency_response(model_obj, freq_list)
        
        # 格式化输出
        if output_format.lower() == 'json':
            import json
            result = json.dumps({
                "model": model_obj.to_dict(),
                "frequency_response": {
                    "frequencies": freq_response["frequencies"],
                    "magnitudes": [float(m) for m in freq_response["magnitudes"]],
                    "phases": [float(p) for p in freq_response["phases"]],
                    "magnitude_db": [float(m) for m in freq_response["magnitude_db"]]
                }
            }, indent=2, ensure_ascii=False)
        else:
            lines = [f"{model_obj.name} 频率响应", "=" * 40]
            lines.append(f"{'频率':<10} {'幅度':<15} {'相位':<15} {'幅度(dB)':<15}")
            lines.append("-" * 60)
            
            for i, freq in enumerate(freq_response["frequencies"]):
                mag = freq_response["magnitudes"][i]
                phase = freq_response["phases"][i]
                mag_db = freq_response["magnitude_db"][i]
                lines.append(f"{freq:<10.3f} {mag:<15.6f} {phase:<15.6f} {mag_db:<15.3f}")
            
            result = "\n".join(lines)
        
        # 输出结果
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            click.echo(f"频率响应已保存到: {output}")
        else:
            click.echo(result)
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--model', '-m', required=True,
              help='模型字符串，如 "ARIMA(2,1,1)" 或 "SARIMA(2,1,1)(1,1,1,12)"')
@click.option('--output', '-o', type=click.Path(),
              help='输出文件路径')
def stability(model: str, output: Optional[str]):
    """
    分析模型稳定性
    """
    try:
        # 解析模型
        model_obj = ModelParser.parse_from_string(model)
        
        # 稳定性分析
        deriver = TransferFunctionDeriver()
        stability_result = deriver.analyze_stability(model_obj)
        
        # 格式化输出
        lines = [f"{model_obj.name} 稳定性分析", "=" * 40]
        lines.append(f"系统稳定性: {'稳定' if stability_result['is_stable'] else '不稳定'}")
        lines.append(f"最大极点模长: {stability_result['max_pole_magnitude']:.6f}")
        lines.append(f"稳定性裕度: {stability_result['stability_margin']:.6f}")
        lines.append("")
        
        if stability_result['poles']:
            lines.append("极点:")
            for i, pole in enumerate(stability_result['poles']):
                lines.append(f"  p_{i+1} = {pole:.6f} (|p_{i+1}| = {abs(pole):.6f})")
        
        if stability_result['zeros']:
            lines.append("")
            lines.append("零点:")
            for i, zero in enumerate(stability_result['zeros']):
                lines.append(f"  z_{i+1} = {zero:.6f}")
        
        if not stability_result['is_stable']:
            lines.append("")
            lines.append("警告: 系统不稳定！存在模长大于等于1的极点。")
        
        result = "\n".join(lines)
        
        # 输出结果
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            click.echo(f"稳定性分析已保存到: {output}")
        else:
            click.echo(result)
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@main.command()
def examples():
    """
    显示使用示例
    """
    examples_text = """
使用示例:

1. 分析简单ARIMA模型:
   tsm-analyzer analyze -m "ARIMA(2,1,1)"

2. 分析带参数的ARIMA模型:
   tsm-analyzer analyze -m "ARIMA(2,1,1)" --include-analysis

3. 分析SARIMA模型并输出LaTeX格式:
   tsm-analyzer analyze -m "SARIMA(2,1,1)(1,1,1,12)" --format latex

4. 从配置文件分析:
   tsm-analyzer analyze -f model_config.json --format json -o result.json

5. 交互式输入:
   tsm-analyzer analyze --interactive

6. 计算脉冲响应:
   tsm-analyzer impulse -m "ARIMA(2,1,1)" --max-lag 10

7. 计算频率响应:
   tsm-analyzer frequency -m "ARIMA(2,1,1)" --frequencies "0,0.1,0.2,0.3,0.4,0.5"

8. 稳定性分析:
   tsm-analyzer stability -m "ARIMA(2,1,1)"

配置文件格式 (JSON):
{
  "model_type": "ARIMA",
  "p": 2,
  "d": 1,
  "q": 1,
  "ar_params": [0.5, -0.3],
  "ma_params": [0.2],
  "constant": 0
}

配置文件格式 (YAML):
model_type: SARIMA
p: 2
d: 1
q: 1
P: 1
D: 1
Q: 1
m: 12
ar_params: [0.5, -0.3]
ma_params: [0.2]
seasonal_ar_params: [0.8]
seasonal_ma_params: [0.4]
"""
    click.echo(examples_text)


if __name__ == '__main__':
    main()
