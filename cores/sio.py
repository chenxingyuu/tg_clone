import socketio
from fastapi_socketio import SocketManager

from cores.config import settings

# 使用 Redis 作为消息传递的后端
redis_manager = socketio.AsyncRedisManager(settings.redis.db_url)

# 定义 Socket.IO 实例
sio: SocketManager = None


# 将 Socket.IO 附加到 FastAPI 应用的函数
def attach_socketio(app):
    global sio
    sio = SocketManager(app=app, client_manager=redis_manager)
