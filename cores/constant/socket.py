from enum import Enum
from typing import Optional

from pydantic import BaseModel


class WsMessage(BaseModel):
    event: str
    data: dict
    room: Optional[str] = None  # 可选


class SioEvent(Enum):
    # 前端发送
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    ENTER_ROOM = "enter_room"
    LEAVE_ROOM = "leave_room"
    CLOSE_ROOM = "close_room"

    # 后端发送
    SYSTEM_NOTIFY = "system_notify"  # 系统通知、浏览器通知
    NOTIFY_MESSAGE = "notify_message"  # 系统内部通知
