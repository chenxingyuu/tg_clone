import asyncio
import functools
import os.path
import time
from datetime import datetime, timedelta
from inspect import isawaitable

from telethon import TelegramClient

from app.tg.models import Account
from cores.config import settings
from cores.log import LOG
from cores.redis import ASYNC_REDIS
from crontabs.base import BaseDBScript


class AccountLogin(BaseDBScript):
    """
    登录账号，初始化客户端
    对于第一次登录的账号，需要打开TG客户端，获取验证码，输入验证码，登录账号
    之后登录状态会存储到 session 文件中，下次登录时会自动读取 session 文件
    """

    def __init__(self):
        self.redis = ASYNC_REDIS
        self.code_name_prefix = "tg:code:{phone}"

    @classmethod
    def get_client(cls, account: Account) -> TelegramClient:
        session = os.path.join(settings.tg.session_path, f"{account.phone}.session")
        return TelegramClient(
            session=session,
            api_id=account.api_id,
            api_hash=account.api_hash,
            timeout=3
        )

    def get_code_from_redis(self, phone, timeout=60):
        """从 redis 中获取验证码"""
        LOG.info(f"Get code from redis. Phone: {phone}")
        now = datetime.now()
        end = now + timedelta(seconds=timeout)
        name = self.code_name_prefix.format(phone=phone)
        while now < end:
            if code := self.redis.get(name):
                self.redis.delete(name)
                LOG.info(f"Get code from redis. Phone: {phone}, Code: {code}")
                return code
            else:
                LOG.info(f"Code not found in redis. Name: {name}")
            time.sleep(1)
            now = datetime.now()
        return None

    async def __call__(self, *args, **kwargs):
        account_list = await Account.all()

        for account in account_list:
            # 获取客户端
            client = self.get_client(account)

            # 如果 session 文件不存在，则需要重新登录
            LOG.info(f"Start client. Account: {account.phone}")

            # 验证码，从redis中获取验证码
            code_callback = functools.partial(self.get_code_from_redis, account.phone)

            if account.password:
                LOG.info(f"Start client with password. Account: {account.phone}")
                conn = client.start(phone=account.phone, password=account.password, code_callback=code_callback)
            else:
                LOG.info(f"Start client with code. Account: {account.phone}", code_callback=code_callback)
                conn = client.start(phone=account.phone)

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
