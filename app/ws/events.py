from jose import JWTError
from passlib.exc import InvalidTokenError

from cores.constant.socket import WsMessage, SioEvent
from cores.constant.tg import ACCOUNT_LOGIN_CHANNEL
from cores.jwt import verify_token
from cores.log import LOG
from cores.redis import ASYNC_REDIS
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
async def close(sid: str, message: WsMessage):
    await sio.close_room(sid=sid, room=message.room)
    LOG.info(f"客户端 {sid} 关闭房间 {message.room}")


@sio.on(SioEvent.TG_ACCOUNT_LOGIN.value)
async def tg_account_login(sid: str, phone: str):
    LOG.info(f"客户端 {sid} 请求登录账户 {phone}")
    # 进入房间
    LOG.info(f"客户端 {sid} 进入房间 {phone}")
    await sio.enter_room(sid=sid, room=phone)
    # 通知中台 crontabs/account/login.py 启动登录程序
    LOG.info(f"通知中台启动登录程序 {phone}")
    await ASYNC_REDIS.publish(ACCOUNT_LOGIN_CHANNEL, phone)
    # 通知客户端正在启动登录
    LOG.info(f"通知客户端正在启动登录 {phone}")
    await sio.emit(SioEvent.TG_ACCOUNT_LOGIN_UPDATE.value, data=f"{phone}正在启动登录", room=phone)
