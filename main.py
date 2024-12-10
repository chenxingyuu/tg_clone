import contextlib
import logging
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from cores.config import settings
from cores.model import TORTOISE_ORM, init_db, close_db
from cores.scope import init_scopes
from cores.sio import attach_socketio

logging.basicConfig(level=logging.DEBUG)


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # 应用启动时的初始化
    await init_db()
    # 在这里注册 Tortoise，以确保在路由中使用 Tortoise 之前数据库已经初始化
    register_tortoise(
        _app,
        config=TORTOISE_ORM,
        generate_schemas=False,
        add_exception_handlers=True,
    )

    # 初始化全局的 scopes
    await init_scopes()

    # 包含路由
    from app.common.urls import router as common_router
    from app.system.urls import router as system_router
    from app.ws.urls import router as sio_router

    _app.include_router(common_router, prefix=settings.app.api_version)
    _app.include_router(system_router, prefix=settings.app.api_version)
    _app.include_router(sio_router, prefix=settings.app.api_version)

    yield
    # 应用关闭时的清理
    await close_db()


app = FastAPI(
    title=settings.app.project_name,
    debug=settings.app.debug,
    lifespan=lifespan,
    docs_url=settings.app.doc_path,
    redoc_url=None,
)

attach_socketio(app)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.app.host, port=settings.app.port, reload=settings.app.debug)
