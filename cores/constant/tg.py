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
