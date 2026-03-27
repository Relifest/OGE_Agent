import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import agent
from utils.config_handler import server_conf
from utils.logger_handler import logger

# 创建FastAPI应用
app = FastAPI(
    title="OGE智能助手API",
    description="基于LangChain的OGE智能助手服务接口",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("OGE智能助手API服务启动中...")
    logger.info(f"服务配置: {server_conf.get('server', {})}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("OGE智能助手API服务正在关闭...")


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "OGE智能助手API服务",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn

    server_config = server_conf.get("server", {})
    uvicorn.run(
        "app.main:app",
        host=server_config.get("host", "0.0.0.0"),
        port=server_config.get("port", 8000),
        reload=server_config.get("reload", True),
        log_level=server_config.get("log_level", "info")
    )
