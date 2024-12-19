import asyncio

from app.tg.models import Account, Dialog
from cores.constant.tg import DialogType
from cores.log import LOG
from crontabs.base import TGClientMethod, BaseDBScript


class AccountChannelInfoUpdate(BaseDBScript, TGClientMethod):
    """
    更新账号频道信息
    """

    def __init__(self):
        pass

    @classmethod
    def get_dialog_type(cls, dialog):
        if dialog.is_user:
            return DialogType.USER
        elif dialog.is_group:
            return DialogType.GROUP
        else:
            return DialogType.CHANNEL

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
            dialog_type = self.get_dialog_type(dialog)
            dialog_title = dialog.name
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
        account_list = await Account.filter(status=True).all()
        await asyncio.gather(*[self.update_channel_info(account) for account in account_list])


async def main():
    server = AccountChannelInfoUpdate()

    # 初始化数据库
    await server.init_db()

    await server()

    # 关闭数据库
    await server.close_db()


if __name__ == '__main__':
    asyncio.run(main())
