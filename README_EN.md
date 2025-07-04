[English](README_EN.md) | [中文](README.md)

# Time Series Model Transfer Function Analyzer

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

A Python library for automatically deriving transfer functions of time series models. Supports parameterized input and symbolic derivation of transfer functions for ARIMA and SARIMA models.

## 🚀 Core Features

### 1. Model Parameter Input & Parsing
- Supports multiple input methods: command-line arguments, config files (JSON/YAML), interactive input
- Automatic validation of model parameters
- Supports symbolic and numeric parameters

### 2. Automatic Transfer Function Derivation & Generation
- Symbolic computation for automatic derivation of transfer function expressions
- Converts ARIMA/SARIMA models to polynomial ratio form in lag operator B
- Supports LaTeX, plain text, JSON, and more output formats

### 3. Advanced Analysis Functions
- Stability analysis (poles, zeros calculation)
- Impulse response computation
- Frequency response analysis
- System characteristics evaluation

## 📦 Installation

### Using uv (Recommended)
```bash
uv add time-series-model-transfer-function-analyzer
```

### Using pip
```bash
pip install time-series-model-transfer-function-analyzer
```

### Install from Source
```bash
git clone https://github.com/zym9863/time-series-model-transfer-function-analyzer.git
cd time-series-model-transfer-function-analyzer
uv sync
```

## 🎯 Quick Start

### FastAPI Web Service

This project provides a complete FastAPI web service for time series model analysis via HTTP API.

#### Start the Service

```bash
# Method 1: Use the startup script
python scripts/start_api.py

# Method 2: Use uvicorn directly
uvicorn src.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload

# Method 3: Use convenience script
# Windows
scripts/start_api.bat

# Linux/macOS
chmod +x scripts/start_api.sh
./scripts/start_api.sh
```

#### Access API Documentation

After starting the service, visit:

- **API Docs (Swagger UI)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/api/v1/health

#### API Usage Examples

**1. Health Check**
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**2. ARIMA Model Analysis**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze/arima" \
  -H "Content-Type: application/json" \
  -d '{
    "p": 2,
    "d": 1,
    "q": 1,
    "ar_params": [0.5, -0.3],
    "ma_params": [0.2],
    "include_stability": true
  }'
```

**3. Analyze by Model String**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze/model-string" \
  -H "Content-Type: application/json" \
  -d '{
    "model_string": "ARIMA(2,1,1)",
    "include_stability": true,
    "include_impulse": true
  }'
```

**4. Get Supported Model Types**
```bash
curl -X GET "http://localhost:8000/api/v1/models"
```

### Command Line Tool

#### Basic Usage
```bash
# Analyze a simple ARIMA model
tsm-analyzer analyze -m "ARIMA(2,1,1)"

# Analyze SARIMA model and output LaTeX format
tsm-analyzer analyze -m "SARIMA(2,1,1)(1,1,1,12)" --format latex

# Analyze from config file
tsm-analyzer analyze -f examples/arima_example.json --include-analysis

# Interactive input
tsm-analyzer analyze --interactive
```

#### Advanced Analysis
```bash
# Compute impulse response
tsm-analyzer impulse -m "ARIMA(2,1,1)" --max-lag 10

# Compute frequency response
tsm-analyzer frequency -m "ARIMA(2,1,1)" --frequencies "0,0.1,0.2,0.3,0.4,0.5"

# Stability analysis
tsm-analyzer stability -m "ARIMA(2,1,1)"
```

### Python API

#### Basic Usage
```python
from time_series_analyzer import TimeSeriesAnalyzer

# Create analyzer
analyzer = TimeSeriesAnalyzer()

# Create ARIMA model
model = analyzer.create_arima_model(
    p=2, d=1, q=1,
    ar_params=[0.5, -0.3],
    ma_params=[0.2]
)

# Derive transfer function
transfer_func = analyzer.derive_transfer_function(model)
print(f"Transfer Function: {transfer_func}")

# Analyze stability
stability = analyzer.analyze_stability(model)
print(f"System Stability: {stability['is_stable']}")
```

#### Convenience Functions
```python
from time_series_analyzer import analyze_arima, parse_and_analyze

# Quick ARIMA analysis
result = analyze_arima(
    p=2, d=1, q=1,
    ar_params=[0.5, -0.3],
    ma_params=[0.2],
    include_stability=True,
    include_impulse=True
)

# Parse and analyze from string
result = parse_and_analyze(
    "SARIMA(2,1,1)(1,1,1,12)",
    include_stability=True
)
```

## 📋 Supported Models

### ARIMA Model
- **ARIMA(p,d,q)**: Autoregressive Integrated Moving Average
- Supports arbitrary order for AR, I, MA parts
- Automatic differencing

### SARIMA Model
- **SARIMA(p,d,q)(P,D,Q,m)**: Seasonal ARIMA
- Supports seasonal and non-seasonal parameters
- Flexible seasonal period

## 🔧 Config File Format

### JSON Format
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

### YAML Format
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

## 📊 Output Formats

### LaTeX Math Expression
```latex
\section{ARIMA(2,1,1) Model Analysis}

\subsection{Transfer Function}
$H(B) = \frac{1 + 0.2B}{(1 - 0.5B + 0.3B^2)(1-B)}$
```

### Plain Text
```
==================================================
ARIMA(2,1,1) Model Analysis
==================================================

Transfer Function:
------------------------------
H(B) = (1 + 0.2*B) / ((1 - 0.5*B + 0.3*B**2)*(1 - B))

Stability Analysis:
------------------------------
System Stability: Stable
Max Pole Modulus: 0.8660
```

### JSON Structured Data
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

## 🧮 Mathematical Principles

### ARIMA Model Transfer Function

For ARIMA(p,d,q):
```
φ(B)(1-B)^d X_t = θ(B)ε_t
```

Transfer function:
```
H(B) = θ(B) / [φ(B)(1-B)^d]
```

Where:
- φ(B) = 1 - φ₁B - φ₂B² - ... - φₚBᵖ (AR polynomial)
- θ(B) = 1 + θ₁B + θ₂B² + ... + θₑBᵠ (MA polynomial)
- (1-B)^d is the differencing operator

### SARIMA Model Transfer Function

For SARIMA(p,d,q)(P,D,Q,m):
```
φ(B)Φ(B^m)(1-B)^d(1-B^m)^D X_t = θ(B)Θ(B^m)ε_t
```

Transfer function:
```
H(B) = θ(B)Θ(B^m) / [φ(B)Φ(B^m)(1-B)^d(1-B^m)^D]
```

## 🔍 Example Analysis

### Example 1: ARIMA(1,1,1)

```python
from time_series_analyzer import parse_and_analyze

# Analyze ARIMA(1,1,1)
result = parse_and_analyze(
    "ARIMA(1,1,1)",
    include_stability=True,
    include_impulse=True,
    max_lag=10
)

print("Model Info:")
print(f"  Type: {result['model']['model_type']}")
print(f"  Params: p={result['model']['parameters']['p']}, "
      f"d={result['model']['parameters']['d']}, "
      f"q={result['model']['parameters']['q']}")

print("\nTransfer Function:")
print(f"  Numerator: {result['transfer_function']['numerator']}")
print(f"  Denominator: {result['transfer_function']['denominator']}")

print(f"\nStability: {'Stable' if result['stability']['is_stable'] else 'Unstable'}")
```

### Example 2: Seasonal Model Analysis

```python
from time_series_analyzer import TimeSeriesAnalyzer

analyzer = TimeSeriesAnalyzer()

# Create SARIMA model
model = analyzer.create_sarima_model(
    p=1, d=1, q=1,      # Non-seasonal part
    P=1, D=1, Q=1, m=12, # Seasonal part (monthly)
    ar_params=[0.7],
    ma_params=[0.3],
    seasonal_ar_params=[0.5],
    seasonal_ma_params=[0.2]
)

# Generate full report
report = analyzer.generate_report(
    model,
    format='text',
    include_analysis=True
)

print(report)
```

## 🛠️ Development

### Environment Setup
```bash
# Clone repo
git clone https://github.com/zym9863/time-series-model-transfer-function-analyzer.git
cd time-series-model-transfer-function-analyzer

# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Code formatting
uv run black src tests
uv run isort src tests

# Type checking
uv run mypy src
```

### Project Structure
```
time-series-model-transfer-function-analyzer/
├── src/
│   ├── time_series_analyzer/    # Core analysis library
│   │   ├── __init__.py          # Main API exports
│   │   ├── models.py            # ARIMA/SARIMA model definitions
│   │   ├── transfer_function.py # Transfer function engine
│   │   ├── parsers.py           # Input parsers
│   │   ├── formatters.py        # Output formatters
│   │   ├── api.py              # High-level API
│   │   └── cli.py              # CLI tool
│   └── api/                     # FastAPI Web service
│       ├── __init__.py
│       ├── app.py              # FastAPI app main file
│       ├── config.py           # Config management
│       ├── middleware.py       # Middleware
│       ├── schemas.py          # Request/response models
│       └── routers/            # API routers
│           ├── __init__.py
│           ├── analysis.py     # Analysis service router
│           ├── health.py       # Health check router
│           └── models.py       # Model management router
├── scripts/                     # Startup scripts
│   ├── start_api.py            # Python startup script
│   ├── start_api.bat           # Windows batch script
│   └── start_api.sh            # Linux/macOS script
├── tests/                       # Test suite
├── examples/                    # Example config files
├── docs/                   # Documentation
└── pyproject.toml          # Project config
```

## 📚 API Reference

### Core Classes

#### `TimeSeriesAnalyzer`
Main analyzer class providing all analysis functions.

**Methods:**
- `create_arima_model()` - Create ARIMA model
- `create_sarima_model()` - Create SARIMA model
- `derive_transfer_function()` - Derive transfer function
- `analyze_stability()` - Stability analysis
- `compute_impulse_response()` - Compute impulse response
- `compute_frequency_response()` - Compute frequency response
- `generate_report()` - Generate analysis report

#### `ARIMAModel` / `SeasonalARIMAModel`
Model data classes, validated with Pydantic.

#### `TransferFunction`
Transfer function representation, includes numerator, denominator polynomials, and analysis methods.

### Convenience Functions

- `analyze_arima()` - Quick ARIMA analysis
- `analyze_sarima()` - Quick SARIMA analysis
- `parse_and_analyze()` - Parse and analyze from string

### FastAPI Endpoints

#### Health Check
- `GET /api/v1/health` - Service health check

#### Model Management
- `GET /api/v1/models` - Get supported model types
- `GET /api/v1/models/validate/{model_string}` - Validate model string

#### Analysis Services
- `POST /api/v1/analyze/arima` - Analyze ARIMA model
- `POST /api/v1/analyze/sarima` - Analyze SARIMA model
- `POST /api/v1/analyze/model-string` - Analyze by model string
- `GET /api/v1/analyze/transfer-function/{model_string}` - Get transfer function only
- `GET /api/v1/analyze/stability/{model_string}` - Get stability analysis only

#### Request/Response Format

All API endpoints use JSON for data exchange. For detailed request and response formats, see:
- **Swagger UI Docs**: http://localhost:8000/docs
- **ReDoc Docs**: http://localhost:8000/redoc

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Ensure all tests pass
- Add appropriate test coverage
- Follow code style guidelines
- Update relevant documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [SymPy](https://www.sympy.org/) - Symbolic math
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Click](https://click.palletsprojects.com/) - CLI
- [Rich](https://rich.readthedocs.io/) - Terminal formatting

## 📞 Contact

- Project Home: https://github.com/zym9863/time-series-model-transfer-function-analyzer
- Issues: https://github.com/zym9863/time-series-model-transfer-function-analyzer/issues

---

**Note**: This is an academic research tool, mainly for teaching and research purposes. Please fully test before using in production.
