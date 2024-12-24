import contextlib
from typing import AsyncIterator

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from cores.config import settings
from cores.log import LOG
from cores.model import init_db, TORTOISE_ORM, close_db
from cores.scope import init_scopes
from cores.sio import attach_socketio


def register_routes(_app: FastAPI):
    LOG.info("Registering routes...")
    from app.common.urls import router as common_router
    from app.system.urls import router as system_router
    from app.tg.urls import router as tg_router
    from app.ws.urls import router as sio_router

    _app.include_router(common_router, prefix=settings.app.api_version)
    _app.include_router(system_router, prefix=settings.app.api_version)
    _app.include_router(tg_router, prefix=settings.app.api_version)
    _app.include_router(sio_router, prefix=settings.app.api_version)
    LOG.info("Routes registered.")


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    LOG.info("Starting application lifespan...")
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

    # 注册路由
    register_routes(_app)

    # 注册 Socket.IO
    attach_socketio(_app)

    # 通过 yield 将控制权交给 FastAPI
    yield

    # 应用关闭时的清理
    await close_db()


def make_app():
    return FastAPI(
        title=settings.app.project_name,
        debug=settings.app.debug,
        lifespan=lifespan,
        docs_url=settings.app.doc_path,
        redoc_url=None,
        openapi_url=f"{settings.app.doc_path}.json",
    )
