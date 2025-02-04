from dataclasses import dataclass
from enum import IntEnum


class AccountStatus(IntEnum):
    """
    账号状态
    """
    NORMAL = 1  # 正常
    SUSPENDED = 2  # 暂停
    EXPIRED = 3  # 过期
    FAILED = 4  # 失败


class DialogType(IntEnum):
    """
    对话类型
    """
    USER = 1
    GROUP = 2
    CHANNEL = 3
    CHAT = 4
    CHAT_FORBIDDEN = 5


ACCOUNT_LOGIN_CHANNEL = "tg:login_task:channel"
ACCOUNT_LOGIN_CODE = "tg:code:{phone}"

ACCOUNT_DIALOG_SYNC_CHANNEL = "tg:dialog_sync_task:channel"


class DialogSyncType(IntEnum):
    """
    对话同步类型
    """
    AUTO = 1  # 自动同步
    MANUAL = 2  # 手动同步


class DialogSyncStatus(IntEnum):
    """
    对话同步启用状态
    """
    ENABLE = 1  # 启用
    DISABLE = 0  # 禁用


@dataclass
class DialogSyncSetting:
    """
    对话同步设置
    """
    message_reversed: bool = False  # 消息是否倒序
    only_latest_message: bool = False  # 只同步最新消息
