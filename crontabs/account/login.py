import asyncio
import os.path
from inspect import isawaitable

from telethon import TelegramClient

from app.tg.models import Account
from cores.config import settings
from cores.log import LOG
from crontabs.base import BaseDBScript


class AccountLogin(BaseDBScript):
    """
    登录账号，初始化客户端
    对于第一次登录的账号，需要打开TG客户端，获取验证码，输入验证码，登录账号
    之后登录状态会存储到 session 文件中，下次登录时会自动读取 session 文件
    """

    @classmethod
    def get_client(cls, account: Account) -> TelegramClient:
        session = os.path.join(settings.tg.session_path, f"{account.phone}.session")
        return TelegramClient(
            session=session,
            api_id=account.api_id,
            api_hash=account.api_hash,
            timeout=3
        )

    async def __call__(self, *args, **kwargs):
        account_list = await Account.all()

        for account in account_list:
            # 获取客户端
            client = self.get_client(account)

            # 如果 session 文件不存在，则需要重新登录
            LOG.info(f"Start client. Account: {account.phone}")

            conn = client.start(phone=account.phone, force_sms=True)
            if isawaitable(conn):
                await conn

            LOG.info(f"Client started successfully. Account: {account.phone}")
            me = await client.get_me()
            LOG.info(me.to_dict())

            # 保存账号信息
            account.username = me.username or ""
            account.first_name = me.first_name or ""
            account.last_name = me.last_name or ""
            account.tg_id = me.id
            await account.save()
            LOG.info(f"Account saved. Account: {account}")


async def main():
    server = AccountLogin()

    # 初始化数据库
    await server.init_db()

    await server()

    # 关闭数据库
    await server.close_db()


if __name__ == '__main__':
    asyncio.run(main())
