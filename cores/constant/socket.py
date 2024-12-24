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
    TG_ACCOUNT_LOGIN = "tg_account_login"  # 账户登录
    TG_ACCOUNT_LOGIN_CODE = "tg_account_send_code"  # 账户登录验证码
    TG_ACCOUNT_DIALOG_INFO_SYNC = "tg_account_dialog_info_sync"  # 账户对话信息同步

    # 后端发送
    SYSTEM_NOTIFY = "system_notify"  # 系统通知、浏览器通知
    NOTIFY_MESSAGE = "notify_message"  # 系统内部通知
    TG_ACCOUNT_LOGIN_UPDATE = "tg_account_login_update"  # 账户登录状态更新
    TG_ACCOUNT_LOGIN_SUCCESS = "tg_account_login_success"  # 账户登录成功
    TG_ACCOUNT_LOGIN_ERROR = "tg_account_login_error"  # 账户登录失败
    TG_ACCOUNT_DIALOG_INFO_SYNC_UPDATE = "tg_account_dialog_info_sync_update"  # 账户对话信息同步状态更新
