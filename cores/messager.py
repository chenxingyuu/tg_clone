from ghkit.messenger.feishu import FeishuMessageType
from ghkit.messenger.feishu.custom_bot import FeishuCustomBotMessageSender

from cores.config import settings


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

    async def async_send_alarm(self, message):
        await self.default_message_sender.async_send(message=message, message_type=FeishuMessageType.INTERACTIVE)


MESSAGE_FACTORY = MessageSenderFactory()