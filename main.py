import uvicorn
from starlette.middleware.cors import CORSMiddleware

from cores.config import settings
from cores.fastapi_app import make_app
from cores.middlewares.exception_handler import ExceptionHandlerMiddleware

app = make_app()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 添加自定义异常处理中间件
app.add_middleware(ExceptionHandlerMiddleware)

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.app.host, port=settings.app.port, reload=settings.app.debug)
