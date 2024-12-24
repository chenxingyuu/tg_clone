import asyncio

from telethon.tl.types import Chat, ChatForbidden, User, Channel

from app.tg.models import Account, Dialog
from cores.constant.tg import DialogType, ACCOUNT_DIALOG_SYNC_CHANNEL
from cores.log import LOG
from cores.redis import REDIS
from crontabs.base import TGClientMethod, BaseDBScript


class AccountDialogInfoSync(BaseDBScript, TGClientMethod):
    """
    同步账号对话信息
    """

    def __init__(self):
        self.async_redis = REDIS
        self.task_channel_name = ACCOUNT_DIALOG_SYNC_CHANNEL
        self.pub = self.async_redis.pubsub()

    @classmethod
    def get_dialog_type(cls, dialog):
        if isinstance(dialog, Chat):
            return DialogType.CHAT
        elif isinstance(dialog, ChatForbidden):
            return DialogType.CHAT_FORBIDDEN
        elif isinstance(dialog, User):
            return DialogType.USER
        elif isinstance(dialog, Channel):
            return DialogType.CHANNEL
        else:
            return DialogType.GROUP

    async def update_channel_info(self, account: Account):
        # 获取客户端
        client = self.get_client(account)
        LOG.info(f"Start client. Account: {account.phone}")
        # 启动客户端
        await self.start_client(client=client, account=account)
        # 获取频道信息
        async for dialog in client.iter_dialogs():
            # 转换为实体
            dialog_entity = await client.get_entity(dialog.id)
            LOG.info(f"Dialog: {dialog_entity.to_dict()}")

            # 获取对话类型
            dialog_type = self.get_dialog_type(dialog_entity)
            # 获取对话标题和用户名
            if dialog_type in (DialogType.CHAT, DialogType.CHAT_FORBIDDEN):
                dialog_title, dialog_username = dialog_entity.title
            elif dialog_type == DialogType.USER:
                dialog_title = dialog_entity.first_name
                dialog_username = dialog_entity.username
            else:
                dialog_title = dialog_entity.title
                dialog_username = dialog_entity.username

            # 判断是否存在
            dialog_info, created = await Dialog.update_or_create(
                tg_id=dialog.id,
                account_id=account.id,
                defaults={
                    "title": dialog_title,
                    "username": dialog_username,
                    "type": dialog_type,
                }
            )
            if created:
                LOG.info(f"Dialog created. Dialog: {dialog_info.username}, Created: {created}")
            else:
                LOG.info(f"Dialog updated. Dialog: {dialog_info.username}, Created: {created}")
        client.disconnect()

    async def __call__(self, *args, **kwargs):
        """
        任务逻辑
        :param args:
        :param kwargs:
        :return:
        """
        # 订阅任务通道
        LOG.info(f"Subscribe task channel. Channel: {self.task_channel_name}")
        self.pub.subscribe(self.task_channel_name)
        # 监听任务
        for message in self.pub.listen():
            LOG.info(f"Receive message. Message: {message}")
            if message["type"] == "message":
                phone = message["data"]
                LOG.info(f"Receive phone. Phone: {phone}")
                if account := await Account.get_or_none(phone=phone):
                    LOG.info(f"Account found. Phone: {phone}")
                    await self.update_channel_info(account)
                else:
                    LOG.error(f"Account not found. Phone: {phone}")


async def main():
    server = AccountDialogInfoSync()

    # 初始化数据库
    await server.init_db()

    await server()

    # 关闭数据库
    await server.close_db()


if __name__ == '__main__':
    asyncio.run(main())
