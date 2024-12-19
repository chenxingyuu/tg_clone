import asyncio
import functools
import time
from datetime import datetime, timedelta

from app.tg.models import Account
from cores.log import LOG
from cores.redis import REDIS
from crontabs.base import BaseDBScript, TGClientMethod


class AccountLogin(BaseDBScript, TGClientMethod):
    """
    登录账号，初始化客户端
    对于第一次登录的账号，需要打开TG客户端，获取验证码，输入验证码，登录账号
    之后登录状态会存储到 session 文件中，下次登录时会自动读取 session 文件
    """

    def __init__(self):
        self.redis = REDIS
        self.code_name_prefix = "tg:code:{phone}"

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

    async def init_client(self, account: Account):
        # 获取客户端
        client = self.get_client(account)
        # 如果 session 文件不存在，则需要重新登录
        LOG.info(f"Start client. Account: {account.phone}")
        # 验证码，从redis中获取验证码
        code_callback = functools.partial(self.get_code_from_redis, account.phone)
        # 启动客户端
        await self.start_client(client=client, account=account, code_callback=code_callback)
        # 获取账号信息
        me = await client.get_me()
        LOG.info(me.to_dict())
        # 保存账号信息
        account.username = me.username or ""
        account.first_name = me.first_name or ""
        account.last_name = me.last_name or ""
        account.tg_id = me.id
        await account.save()
        LOG.info(f"Account saved. Account: {account}")
        # 关闭客户端
        client.disconnect()

    async def __call__(self, *args, **kwargs):
        """
        任务逻辑
        接收登录请求，初始化客户端
        :param args:
        :param kwargs:
        :return:
        """
        # TODO 通过任务触发，而不是直接调用
        account_list = await Account.all()
        # 初始化客户端
        await asyncio.gather(*(self.init_client(account) for account in account_list))


async def main():
    server = AccountLogin()

    # 初始化数据库
    await server.init_db()

    await server()

    # 关闭数据库
    await server.close_db()


if __name__ == '__main__':
    asyncio.run(main())
