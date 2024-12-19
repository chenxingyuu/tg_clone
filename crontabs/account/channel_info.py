import asyncio

from app.tg.models import Account
from cores.log import LOG
from crontabs.base import TGClientMethod, BaseDBScript


class AccountChannelInfoUpdate(BaseDBScript, TGClientMethod):
    """
    更新账号频道信息
    """

    def __init__(self):
        pass

    async def update_channel_info(self, account: Account):
        # 获取客户端
        client = self.get_client(account)
        LOG.info(f"Start client. Account: {account.phone}")
        # 启动客户端
        await self.start_client(client=client, account=account)
        # 获取频道信息
        channels = await client.get_dialogs()
        for channel in channels:
            if channel.is_channel:
                LOG.info(channel.to_dict())
                # 保存频道信息
                pass
        client.disconnect()

    async def __call__(self, *args, **kwargs):
        account_list = await Account.all()
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
