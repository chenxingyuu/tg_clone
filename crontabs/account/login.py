import asyncio
import functools
import time
from datetime import datetime, timedelta

import socketio

from app.tg.models import Account
from cores.config import settings
from cores.constant.socket import SioEvent
from cores.constant.tg import ACCOUNT_LOGIN_CHANNEL, ACCOUNT_LOGIN_CODE, AccountStatus
from cores.log import LOG
from cores.redis import REDIS
from crontabs.base import BaseDBScript, TGClientMethod

redis_manager = socketio.AsyncRedisManager(settings.redis.db_url)
sio = socketio.AsyncServer(client_manager=redis_manager)


class AccountLogin(BaseDBScript, TGClientMethod):
    """
    登录账号，初始化客户端
    对于第一次登录的账号，需要打开TG客户端，获取验证码，输入验证码，登录账号
    之后登录状态会存储到 session 文件中，下次登录时会自动读取 session 文件
    """

    def __init__(self):
        self.redis = REDIS
        self.async_redis = REDIS
        self.task_channel_name = ACCOUNT_LOGIN_CHANNEL
        self.pub = self.async_redis.pubsub()
        self.code_name_prefix = ACCOUNT_LOGIN_CODE

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
        await self.send_login_update_message(account.phone, f"{account.phone}登录成功，正在获取账号信息...")
        # 获取账号信息
        me = await client.get_me()
        LOG.info(me.to_dict())
        await self.send_login_update_message(account.phone, f"{account.phone}账号信息获取成功，正在保存账号信息...")
        # 保存账号信息
        account.username = me.username or ""
        account.first_name = me.first_name or ""
        account.last_name = me.last_name or ""
        account.status = AccountStatus.NORMAL
        account.tg_id = me.id
        await account.save()
        LOG.info(f"Account saved. Account: {account}")
        await self.send_login_update_message(account.phone, f"{account.phone}账号信息保存成功，正在同步对话信息...")
        # 关闭客户端
        client.disconnect()
        await self.send_login_update_message(account.phone, f"{account.phone}登录成功，关闭客户端...")

    @classmethod
    async def send_login_update_message(cls, phone: str, message: str):
        await sio.emit(SioEvent.TG_ACCOUNT_LOGIN_UPDATE.value, data=message, room=phone)

    @classmethod
    async def send_login_success(cls, phone: str):
        await sio.emit(SioEvent.TG_ACCOUNT_LOGIN_SUCCESS.value, room=phone)

    @classmethod
    async def send_login_error(cls, phone: str):
        await sio.emit(SioEvent.TG_ACCOUNT_LOGIN_ERROR.value, room=phone)

    async def __call__(self, *args, **kwargs):
        """
        任务逻辑
        接收登录请求，初始化客户端
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
                # 发送消息给前端
                await self.send_login_update_message(phone, f"{phone}正在启动登录...")
                # 获取账号
                account = await Account.get(phone=phone)
                await self.send_login_update_message(phone, f"{phone}账号信息获取成功，正在初始化客户端...")
                # 初始化客户端
                await self.init_client(account)
                # 发送登录成功消息
                await self.send_login_success(phone)


async def main():
    server = AccountLogin()

    # 初始化数据库
    await server.init_db()

    await server()

    # 关闭数据库
    await server.close_db()


if __name__ == '__main__':
    asyncio.run(main())
