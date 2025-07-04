#!/usr/bin/env python3
"""
FastAPI服务启动脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from src.api.app import create_app
from src.api.config import settings

def main():
    """启动FastAPI服务"""
    
    print(f"启动 {settings.app_name} v{settings.app_version}")
    print(f"服务地址: http://{settings.host}:{settings.port}")
    print(f"API文档: http://{settings.host}:{settings.port}/docs")
    print(f"调试模式: {'开启' if settings.debug else '关闭'}")
    print("-" * 50)
    
    # 创建应用
    app = create_app()
    
    # 启动服务
    if settings.reload:
        # 开发模式：使用模块字符串启动以支持热重载
        uvicorn.run(
            "src.api.app:create_app",
            factory=True,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level,
            access_log=True
        )
    else:
        # 生产模式：直接使用应用实例
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level,
            access_log=True
        )

if __name__ == "__main__":
    main()
