from ghkit.messenger.feishu import FeishuMessageType
from ghkit.messenger.feishu.custom_bot import FeishuCustomBotMessageSender

from cores.config import settings
from cores.log import LOG


class MessageSenderFactory:
    """消息发送工厂"""

    def __init__(self):
        self.default_message_sender = FeishuCustomBotMessageSender(
            webhook_url=settings.feishu.webhook_url, secret=settings.feishu.secret
        )

    def send(self, text: str, ):
        self.default_message_sender.send(message=text)

    async def async_send(self, text: str, ):
        await self.default_message_sender.async_send(message=text)

    def send_alarm(self, message):
        self.default_message_sender.send(message=message, message_type=FeishuMessageType.INTERACTIVE)


MESSAGE_FACTORY = MessageSenderFactory()


def feishu_alarm(class_name, stack):
    try:
        message_dict = {
            "config": {},
            "i18n_elements": {
                "zh_cn": [
                    {"tag": "markdown", "content": f"**🗳脚本：** {class_name}", "text_align": "left", "text_size": "normal"},
                    {"tag": "markdown", "content": "**👇堆栈：** ", "text_align": "left", "text_size": "normal"},
                    {"tag": "markdown", "content": stack, "text_align": "left", "text_size": "normal"},
                    {
                        "tag": "action",
                        "layout": "default",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {"tag": "plain_text", "content": "收到"},
                                "type": "default",
                                "complex_interaction": True,
                                "width": "default",
                                "size": "medium",
                            }
                        ],
                    },
                ]
            },
            "i18n_header": {
                "zh_cn": {
                    "title": {"tag": "plain_text", "content": "⏰脚本异常"},
                    "subtitle": {"tag": "plain_text", "content": ""},
                    "template": "blue",
                }
            },
        }
        # 发送告警信息
        MESSAGE_FACTORY.send_alarm(message_dict)
    except Exception as e:
        LOG.exception(f"发送告警信息时发生错误: {e}")
