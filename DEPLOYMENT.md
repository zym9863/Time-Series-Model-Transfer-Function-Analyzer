# FastAPI服务部署指南

## 概述

本文档介绍如何部署时间序列模型传递函数分析器的FastAPI Web服务。

## 系统要求

- Python 3.9+
- uv包管理器（推荐）或pip
- 8GB+ RAM（用于复杂的SARIMA模型分析）

## 安装和配置

### 1. 克隆项目

```bash
git clone https://github.com/zym9863/time-series-model-transfer-function-analyzer.git
cd time-series-model-transfer-function-analyzer
```

### 2. 安装依赖

使用uv（推荐）：
```bash
uv sync
```

或使用pip：
```bash
pip install -e .
```

### 3. 环境配置

复制环境配置文件：
```bash
cp .env.example .env
```

根据需要修改`.env`文件中的配置：
```env
# 应用配置
APP_NAME=时间序列模型传递函数分析器 API
DEBUG=false

# 服务器配置
HOST=0.0.0.0
PORT=8000
RELOAD=true

# 日志配置
LOG_LEVEL=info

# CORS配置（生产环境中应该限制具体域名）
CORS_ORIGINS=["*"]
```

## 启动服务

### 开发环境

```bash
# 方法1：使用启动脚本
python scripts/start_api.py

# 方法2：直接使用uvicorn
uvicorn src.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload

# 方法3：使用便捷脚本
# Windows
scripts/start_api.bat

# Linux/macOS
chmod +x scripts/start_api.sh
./scripts/start_api.sh
```

### 生产环境

```bash
# 使用Gunicorn（推荐）
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.app:create_app --bind 0.0.0.0:8000

# 或使用uvicorn
uvicorn src.api.app:create_app --factory --host 0.0.0.0 --port 8000 --workers 4
```

## 服务验证

启动服务后，访问以下地址验证服务状态：

- **健康检查**: http://localhost:8000/api/v1/health
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

## API使用示例

### 使用curl

```bash
# 健康检查
curl -X GET "http://localhost:8000/api/v1/health"

# ARIMA模型分析
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

### 使用Python客户端

```python
from src.api.client import create_client

# 创建客户端
client = create_client("http://localhost:8000")

# 分析ARIMA模型
result = client.analyze_arima(
    p=2, d=1, q=1,
    ar_params=[0.5, -0.3],
    ma_params=[0.2],
    include_stability=True
)
print(result)
```

## Docker部署（可选）

创建Dockerfile：
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install uv && uv sync

EXPOSE 8000

CMD ["python", "scripts/start_api.py"]
```

构建和运行：
```bash
docker build -t time-series-api .
docker run -p 8000:8000 time-series-api
```

## 监控和日志

### 日志配置

服务使用Python标准logging模块，日志级别可通过环境变量`LOG_LEVEL`配置。

### 性能监控

- 每个请求都会记录处理时间
- 响应头中包含`X-Process-Time`字段
- 可以通过`/api/v1/health`端点监控服务状态

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用端口的进程
   netstat -tulpn | grep :8000
   # 或使用lsof
   lsof -i :8000
   ```

2. **依赖安装失败**
   ```bash
   # 清理缓存重新安装
   uv cache clean
   uv sync --reinstall
   ```

3. **内存不足**
   - 减少并发worker数量
   - 限制复杂模型的分析参数

### 日志查看

服务日志会输出到控制台，包含：
- 请求信息
- 错误详情
- 性能指标

## 安全建议

1. **生产环境配置**
   - 设置`DEBUG=false`
   - 限制CORS origins到具体域名
   - 使用HTTPS
   - 配置防火墙规则

2. **资源限制**
   - 设置请求超时
   - 限制请求大小
   - 配置rate limiting

3. **监控**
   - 设置健康检查
   - 监控资源使用
   - 配置告警

## 扩展部署

### 负载均衡

使用Nginx作为反向代理：
```nginx
upstream time_series_api {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://time_series_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 集群部署

可以使用Kubernetes、Docker Swarm等容器编排工具进行集群部署。

## 支持

如有问题，请查看：
- [项目文档](README.md)
- [API文档](http://localhost:8000/docs)
- [GitHub Issues](https://github.com/zym9863/time-series-model-transfer-function-analyzer/issues)
