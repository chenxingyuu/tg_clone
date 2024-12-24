from typing import Optional

import socketio
from fastapi_socketio import SocketManager

from cores.config import settings
from cores.log import LOG

# 使用 Redis 作为消息传递的后端
redis_manager = socketio.AsyncRedisManager(settings.redis.db_url)

# 定义 Socket.IO 实例
sio: Optional[SocketManager] = None


# 将 Socket.IO 附加到 FastAPI 应用的函数
def attach_socketio(app):
    LOG.info("Attaching Socket.IO...")
    global sio
    sio = SocketManager(app=app, client_manager=redis_manager)
    LOG.info("Socket.IO attached.")

    # 在这里注册事件处理器
    from app.ws import events  # noqa
    LOG.info("Socket.IO events registered.")
