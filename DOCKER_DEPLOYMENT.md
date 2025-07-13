# Docker 部署指南

本指南介绍如何使用Docker部署Time Series Analyzer FastAPI服务。

## 文件说明

- `Dockerfile` - 标准Docker构建文件
- `Dockerfile.prod` - 生产环境优化版本（多进程）
- `.dockerignore` - Docker构建忽略文件
- `docker-compose.yml` - Docker Compose配置
- `deploy.sh` - Linux/Mac部署脚本
- `deploy.bat` - Windows部署脚本

## 快速开始

### 方法1: 使用部署脚本（推荐）

**Linux/Mac:**
```bash
# 给脚本执行权限
chmod +x deploy.sh

# 构建镜像
./deploy.sh build

# 运行容器
./deploy.sh run

# 查看日志
./deploy.sh logs

# 停止容器
./deploy.sh stop
```

**Windows:**
```cmd
# 构建镜像
deploy.bat build

# 运行容器
deploy.bat run

# 查看日志
deploy.bat logs

# 停止容器
deploy.bat stop
```

### 方法2: 使用Docker Compose

```bash
# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build
```

### 方法3: 手动Docker命令

```bash
# 构建镜像
docker build -t time-series-analyzer .

# 运行容器
docker run -d \
  --name time-series-analyzer-api \
  -p 8000:8000 \
  --restart unless-stopped \
  time-series-analyzer

# 查看日志
docker logs -f time-series-analyzer-api

# 停止容器
docker stop time-series-analyzer-api
```

## 生产环境部署

对于生产环境，建议使用 `Dockerfile.prod`：

```bash
# 构建生产镜像
docker build -f Dockerfile.prod -t time-series-analyzer:prod .

# 运行生产容器
docker run -d \
  --name time-series-analyzer-prod \
  -p 8000:8000 \
  --restart always \
  --memory="512m" \
  time-series-analyzer:prod
```

## 服务访问

服务启动后，可以通过以下地址访问：

- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/v1/health

## 环境配置

可以通过环境变量配置服务：

```bash
docker run -d \
  --name time-series-analyzer-api \
  -p 8000:8000 \
  -e LOG_LEVEL=debug \
  -e WORKERS=4 \
  time-series-analyzer
```

## 容器管理

### 查看容器状态
```bash
docker ps
```

### 进入容器调试
```bash
docker exec -it time-series-analyzer-api bash
```

### 清理资源
```bash
# 停止并删除容器
docker stop time-series-analyzer-api
docker rm time-series-analyzer-api

# 删除镜像
docker rmi time-series-analyzer

# 或使用部署脚本清理
./deploy.sh clean  # Linux/Mac
deploy.bat clean   # Windows
```

## 监控和日志

### 查看实时日志
```bash
docker logs -f time-series-analyzer-api
```

### 健康检查
```bash
curl http://localhost:8000/api/v1/health
```

### 容器状态监控
```bash
docker stats time-series-analyzer-api
```

## 故障排除

### 端口冲突
如果8000端口被占用，可以改用其他端口：
```bash
docker run -d --name time-series-analyzer-api -p 8080:8000 time-series-analyzer
```

### 内存不足
增加容器内存限制：
```bash
docker run -d --name time-series-analyzer-api -p 8000:8000 --memory="1g" time-series-analyzer
```

### 依赖问题
重新构建镜像：
```bash
docker build --no-cache -t time-series-analyzer .
```

## 开发模式

对于开发环境，可以挂载代码目录实现热重载：

```bash
docker run -d \
  --name time-series-analyzer-dev \
  -p 8000:8000 \
  -v $(pwd)/src:/app/src \
  -e RELOAD=true \
  time-series-analyzer
```

## 多环境部署

### 开发环境
```bash
docker-compose -f docker-compose.yml up -d
```

### 生产环境
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 安全建议

1. **不要在生产环境中使用root用户运行容器**
2. **限制容器资源使用**
3. **定期更新基础镜像**
4. **使用具体的镜像标签而不是latest**
5. **扫描镜像安全漏洞**

```bash
# 安全扫描示例
docker scan time-series-analyzer
```
