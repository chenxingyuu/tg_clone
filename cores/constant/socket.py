from enum import Enum
from typing import Optional

from pydantic import BaseModel


class WsMessage(BaseModel):
    event: str
    data: dict
    room: Optional[str] = None  # 可选


class SioEvent(Enum):
    SYSTEM_NOTIFY = "system_notify"  # 系统通知、浏览器通知
    NOTIFY_MESSAGE = "notify_message"  # 系统内部通知
    POSITION_UPDATE = "position_update"  # 位置更新
