from jose import JWTError
from passlib.exc import InvalidTokenError

from cores.constant.socket import WsMessage, SioEvent
from cores.jwt import verify_token
from cores.log import LOG
from cores.sio import sio


# 使用装饰器注册 connect 事件
@sio.on(SioEvent.CONNECT.value)
async def connect(sid, environ):
    token = environ.get("QUERY_STRING")
    token = token.split("token=")[-1].split("&")[0] if "token=" in token else None
    try:
        payload = verify_token(token)
        username = payload.get("sub")
        LOG.info(f"客户端 {sid = } {username = } 已连接")
        await sio.send("Connection success!", room=sid)
    except (InvalidTokenError, JWTError):
        LOG.error(f"客户端 {sid = } {token = } 连接失败")
        await sio.disconnect(sid=sid)


@sio.on(SioEvent.DISCONNECT.value)
async def disconnect(sid):
    LOG.info(f"客户端 {sid} 已断开连接")


@sio.on(SioEvent.ENTER_ROOM.value)
async def enter(sid, message: WsMessage):
    await sio.enter_room(sid=sid, room=message.room)
    LOG.info(f"enter room {sid = } {message.room = }")


@sio.on(SioEvent.LEAVE_ROOM.value)
async def leave(sid, message: WsMessage):
    await sio.leave_room(sid=sid, room=message.room)
    LOG.info(f"leave room {sid = } {message.room = }")


@sio.on(SioEvent.CLOSE_ROOM.value)
async def close(sid, message: WsMessage):
    await sio.close_room(sid=sid, room=message.room)
    LOG.info(f"客户端 {sid} 关闭房间 {message.room}")


