import asyncio

from app.tg.models import Account, Channel
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
        async for dialog in client.iter_dialogs():
            # 判断是否是频道
            if dialog.is_channel:
                # 转成频道
                channel = await client.get_entity(dialog.id)
                LOG.info(channel.to_dict())
                # 保存频道信息
                channel_info = await Channel.get_or_none(tg_id=channel.id)
                if not channel_info:
                    channel_info = Channel()
                channel_info.title = channel.title
                channel_info.tg_id = channel.id
                channel_info.username = channel.username
                channel_info.account_id = account.id
                await channel_info.save()
                LOG.info(f"Channel info saved. Channel: {channel_info}")

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
