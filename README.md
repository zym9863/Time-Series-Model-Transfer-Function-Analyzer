[English](README_EN.md) | [中文](README.md)

# 时序模型传递函数分析器

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

一个用于自动推导时间序列模型传递函数的Python库。支持ARIMA和SARIMA模型的参数化输入和传递函数的符号推导。

## 🚀 核心功能

### 1. 模型参数化输入与解析
- 支持多种输入方式：命令行参数、配置文件（JSON/YAML）、交互式输入
- 自动验证模型参数的有效性
- 支持符号参数和数值参数

### 2. 传递函数自动推导与生成
- 基于符号计算自动推导传递函数表达式
- 将ARIMA/SARIMA模型转换为关于滞后算子B的多项式比值形式
- 支持LaTeX、纯文本、JSON等多种输出格式

### 3. 高级分析功能
- 稳定性分析（极点、零点计算）
- 脉冲响应函数计算
- 频率响应分析
- 系统特性评估

## 📦 安装

### 使用uv（推荐）
```bash
uv add time-series-model-transfer-function-analyzer
```

### 使用pip
```bash
pip install time-series-model-transfer-function-analyzer
```

### 从源码安装
```bash
git clone https://github.com/zym9863/time-series-model-transfer-function-analyzer.git
cd time-series-model-transfer-function-analyzer
uv sync
```

## 🎯 快速开始

### 命令行工具

#### 基本用法
```bash
# 分析简单ARIMA模型
tsm-analyzer analyze -m "ARIMA(2,1,1)"

# 分析SARIMA模型并输出LaTeX格式
tsm-analyzer analyze -m "SARIMA(2,1,1)(1,1,1,12)" --format latex

# 从配置文件分析
tsm-analyzer analyze -f examples/arima_example.json --include-analysis

# 交互式输入
tsm-analyzer analyze --interactive
```

#### 高级分析
```bash
# 计算脉冲响应
tsm-analyzer impulse -m "ARIMA(2,1,1)" --max-lag 10

# 计算频率响应
tsm-analyzer frequency -m "ARIMA(2,1,1)" --frequencies "0,0.1,0.2,0.3,0.4,0.5"

# 稳定性分析
tsm-analyzer stability -m "ARIMA(2,1,1)"
```

### Python API

#### 基本使用
```python
from time_series_analyzer import TimeSeriesAnalyzer

# 创建分析器
analyzer = TimeSeriesAnalyzer()

# 创建ARIMA模型
model = analyzer.create_arima_model(
    p=2, d=1, q=1,
    ar_params=[0.5, -0.3],
    ma_params=[0.2]
)

# 推导传递函数
transfer_func = analyzer.derive_transfer_function(model)
print(f"传递函数: {transfer_func}")

# 分析稳定性
stability = analyzer.analyze_stability(model)
print(f"系统稳定性: {stability['is_stable']}")
```

#### 便捷函数
```python
from time_series_analyzer import analyze_arima, parse_and_analyze

# 快速分析ARIMA模型
result = analyze_arima(
    p=2, d=1, q=1,
    ar_params=[0.5, -0.3],
    ma_params=[0.2],
    include_stability=True,
    include_impulse=True
)

# 从字符串解析并分析
result = parse_and_analyze(
    "SARIMA(2,1,1)(1,1,1,12)",
    include_stability=True
)
```

## 📋 支持的模型

### ARIMA模型
- **ARIMA(p,d,q)**: 自回归积分移动平均模型
- 支持任意阶数的AR、I、MA部分
- 自动处理差分操作

### SARIMA模型
- **SARIMA(p,d,q)(P,D,Q,m)**: 季节性ARIMA模型
- 支持季节性和非季节性参数
- 灵活的季节性周期设置

## 🔧 配置文件格式

### JSON格式
```json
{
  "model_type": "ARIMA",
  "p": 2,
  "d": 1,
  "q": 1,
  "ar_params": [0.5, -0.3],
  "ma_params": [0.2],
  "constant": 0
}
```

### YAML格式
```yaml
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
```

## 📊 输出格式

### LaTeX数学表达式
```latex
\section{ARIMA(2,1,1) 模型分析}

\subsection{传递函数}
$H(B) = \frac{1 + 0.2B}{(1 - 0.5B + 0.3B^2)(1-B)}$
```

### 纯文本格式
```
==================================================
ARIMA(2,1,1) 模型分析
==================================================

传递函数:
------------------------------
H(B) = (1 + 0.2*B) / ((1 - 0.5*B + 0.3*B**2)*(1 - B))

稳定性分析:
------------------------------
系统稳定性: 稳定
最大极点模长: 0.8660
```

### JSON结构化数据
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "model": {
    "model_type": "ARIMA",
    "parameters": {"p": 2, "d": 1, "q": 1}
  },
  "transfer_function": {
    "numerator": "1 + 0.2*B",
    "denominator": "(1 - 0.5*B + 0.3*B**2)*(1 - B)",
    "poles": [{"real": 0.5, "imag": 0.866}],
    "zeros": [{"real": -5.0, "imag": 0.0}]
  }
}
```

## 🧮 数学原理

### ARIMA模型的传递函数

对于ARIMA(p,d,q)模型：
```
φ(B)(1-B)^d X_t = θ(B)ε_t
```

其传递函数为：
```
H(B) = θ(B) / [φ(B)(1-B)^d]
```

其中：
- φ(B) = 1 - φ₁B - φ₂B² - ... - φₚBᵖ (自回归多项式)
- θ(B) = 1 + θ₁B + θ₂B² + ... + θₑBᵠ (移动平均多项式)
- (1-B)^d 是差分算子

### SARIMA模型的传递函数

对于SARIMA(p,d,q)(P,D,Q,m)模型：
```
φ(B)Φ(B^m)(1-B)^d(1-B^m)^D X_t = θ(B)Θ(B^m)ε_t
```

其传递函数为：
```
H(B) = θ(B)Θ(B^m) / [φ(B)Φ(B^m)(1-B)^d(1-B^m)^D]
```

## 🔍 示例分析

### 示例1：ARIMA(1,1,1)模型

```python
from time_series_analyzer import parse_and_analyze

# 分析ARIMA(1,1,1)模型
result = parse_and_analyze(
    "ARIMA(1,1,1)",
    include_stability=True,
    include_impulse=True,
    max_lag=10
)

print("模型信息:")
print(f"  类型: {result['model']['model_type']}")
print(f"  参数: p={result['model']['parameters']['p']}, "
      f"d={result['model']['parameters']['d']}, "
      f"q={result['model']['parameters']['q']}")

print("\n传递函数:")
print(f"  分子: {result['transfer_function']['numerator']}")
print(f"  分母: {result['transfer_function']['denominator']}")

print(f"\n稳定性: {'稳定' if result['stability']['is_stable'] else '不稳定'}")
```

### 示例2：季节性模型分析

```python
from time_series_analyzer import TimeSeriesAnalyzer

analyzer = TimeSeriesAnalyzer()

# 创建SARIMA模型
model = analyzer.create_sarima_model(
    p=1, d=1, q=1,      # 非季节性部分
    P=1, D=1, Q=1, m=12, # 季节性部分（月度数据）
    ar_params=[0.7],
    ma_params=[0.3],
    seasonal_ar_params=[0.5],
    seasonal_ma_params=[0.2]
)

# 生成完整报告
report = analyzer.generate_report(
    model,
    format='text',
    include_analysis=True
)

print(report)
```

## 🛠️ 开发

### 环境设置
```bash
# 克隆仓库
git clone https://github.com/zym9863/time-series-model-transfer-function-analyzer.git
cd time-series-model-transfer-function-analyzer

# 安装开发依赖
uv sync --dev

# 运行测试
uv run pytest

# 代码格式化
uv run black src tests
uv run isort src tests

# 类型检查
uv run mypy src
```

### 项目结构
```
time-series-model-transfer-function-analyzer/
├── src/time_series_analyzer/
│   ├── __init__.py          # 主要API导出
│   ├── models.py            # ARIMA/SARIMA模型定义
│   ├── transfer_function.py # 传递函数推导引擎
│   ├── parsers.py           # 输入解析器
│   ├── formatters.py        # 输出格式化器
│   ├── api.py              # 高级API接口
│   └── cli.py              # 命令行工具
├── tests/                   # 测试套件
├── examples/               # 示例配置文件
├── docs/                   # 文档
└── pyproject.toml          # 项目配置
```

## 📚 API参考

### 核心类

#### `TimeSeriesAnalyzer`
主要的分析器类，提供所有分析功能。

**方法:**
- `create_arima_model()` - 创建ARIMA模型
- `create_sarima_model()` - 创建SARIMA模型
- `derive_transfer_function()` - 推导传递函数
- `analyze_stability()` - 稳定性分析
- `compute_impulse_response()` - 计算脉冲响应
- `compute_frequency_response()` - 计算频率响应
- `generate_report()` - 生成分析报告

#### `ARIMAModel` / `SeasonalARIMAModel`
模型数据类，使用Pydantic进行验证。

#### `TransferFunction`
传递函数表示类，包含分子、分母多项式和分析方法。

### 便捷函数

- `analyze_arima()` - 快速分析ARIMA模型
- `analyze_sarima()` - 快速分析SARIMA模型
- `parse_and_analyze()` - 从字符串解析并分析

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

### 贡献指南

- 确保所有测试通过
- 添加适当的测试覆盖
- 遵循代码风格指南
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [SymPy](https://www.sympy.org/) - 符号数学计算
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证
- [Click](https://click.palletsprojects.com/) - 命令行界面
- [Rich](https://rich.readthedocs.io/) - 终端美化

## 📞 联系方式

- 项目主页: https://github.com/zym9863/time-series-model-transfer-function-analyzer
- 问题反馈: https://github.com/zym9863/time-series-model-transfer-function-analyzer/issues
- 文档: https://time-series-model-transfer-function-analyzer.readthedocs.io

---

**注意**: 这是一个学术研究工具，主要用于教学和研究目的。在生产环境中使用前请充分测试。