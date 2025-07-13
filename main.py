"""
FastAPI服务主入口
"""

import uvicorn
from src.api.app import create_app

# 创建app实例供uvicorn使用
app = create_app()

def main():
    """启动FastAPI服务"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
