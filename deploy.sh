#!/bin/bash

# 部署脚本 - Time Series Analyzer API

set -e

# 配置变量
IMAGE_NAME="time-series-analyzer"
CONTAINER_NAME="time-series-analyzer-api"
PORT="8000"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 帮助信息
show_help() {
    echo "Usage: $0 [OPTION]"
    echo "Deploy Time Series Analyzer API"
    echo ""
    echo "Options:"
    echo "  build     Build Docker image"
    echo "  run       Run container"
    echo "  stop      Stop container"
    echo "  restart   Restart container"
    echo "  logs      Show container logs"
    echo "  clean     Remove container and image"
    echo "  help      Show this help"
}

# 构建镜像
build_image() {
    echo_info "Building Docker image..."
    docker build -t $IMAGE_NAME .
    echo_info "Image built successfully!"
}

# 运行容器
run_container() {
    echo_info "Stopping existing container if running..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    echo_info "Starting new container..."
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:8000 \
        --restart unless-stopped \
        $IMAGE_NAME
    
    echo_info "Container started successfully!"
    echo_info "API is available at: http://localhost:$PORT"
    echo_info "API documentation: http://localhost:$PORT/docs"
}

# 停止容器
stop_container() {
    echo_info "Stopping container..."
    docker stop $CONTAINER_NAME
    echo_info "Container stopped!"
}

# 重启容器
restart_container() {
    stop_container
    echo_info "Starting container..."
    docker start $CONTAINER_NAME
    echo_info "Container restarted!"
}

# 显示日志
show_logs() {
    echo_info "Showing container logs..."
    docker logs -f $CONTAINER_NAME
}

# 清理
clean() {
    echo_warn "This will remove the container and image. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo_info "Stopping and removing container..."
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
        
        echo_info "Removing image..."
        docker rmi $IMAGE_NAME 2>/dev/null || true
        
        echo_info "Cleanup completed!"
    else
        echo_info "Cleanup cancelled."
    fi
}

# 主逻辑
case "${1:-help}" in
    "build")
        build_image
        ;;
    "run")
        run_container
        ;;
    "stop")
        stop_container
        ;;
    "restart")
        restart_container
        ;;
    "logs")
        show_logs
        ;;
    "clean")
        clean
        ;;
    "help"|*)
        show_help
        ;;
esac
