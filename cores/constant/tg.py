from enum import IntEnum


class DialogType(IntEnum):
    """
    对话类型
    """
    USER = 1
    GROUP = 2
    CHANNEL = 3
    CHAT = 4
    CHAT_FORBIDDEN = 5
