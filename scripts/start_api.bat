@echo off
REM Windows批处理启动脚本

echo 启动时间序列模型传递函数分析器 API服务...

REM 切换到项目根目录
cd /d "%~dp0\.."

REM 激活虚拟环境（如果使用uv）
REM call .venv\Scripts\activate

REM 启动服务
python scripts/start_api.py

pause
