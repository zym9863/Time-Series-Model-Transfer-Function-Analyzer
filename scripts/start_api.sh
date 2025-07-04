#!/bin/bash
# Linux/macOS启动脚本

echo "启动时间序列模型传递函数分析器 API服务..."

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 激活虚拟环境（如果使用uv）
# source .venv/bin/activate

# 启动服务
python scripts/start_api.py
