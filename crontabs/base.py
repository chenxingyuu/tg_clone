import asyncio
import os
import traceback
from inspect import isawaitable

import schedule
import socketio
from schedule import Job
from telethon import TelegramClient, errors
from tortoise import Tortoise

from app.tg.models import Account
from cores.config import settings
from cores.constant.socket import SioEvent
from cores.log import LOG
from cores.messager import MESSAGE_FACTORY
from cores.model import TORTOISE_ORM

redis_manager = socketio.AsyncRedisManager(settings.redis.db_url)
sio = socketio.AsyncServer(client_manager=redis_manager)


class ScriptMeta(type):
    """
    脚本元类
    1. 用于捕获脚本执行过程中的异常
    2. 用于执行定时任务

    """

    def __new__(cls, name, bases, dct):
        # 获取 __call__ 方法
        original_call = dct.get("__call__")

        if asyncio.iscoroutinefunction(original_call):  # 判断是否是异步函数
            async def new_call(self, *args, **kwargs):
                try:
                    # 获取 schedule_job
                    if schedule_job := kwargs.pop("schedule_job", None) or getattr(self, "schedule_job", None):
                        # 防止 schedule_job 被重复调用
                        setattr(self, "schedule_job", None)
                        assert isinstance(schedule_job, Job), "schedule_job 必须是 schedule.Job 类型"

                        # 添加定时任务，支持异步
                        async def wrapped_job():
                            await self(*args, **kwargs)

                        schedule_job.do(lambda: asyncio.create_task(wrapped_job()))

                    # 调用原始的 __call__ 方法
                    return await original_call(self, *args, **kwargs)
                except Exception as e:
                    # 捕获并处理异常
                    self.handle_exception(e, name)

        else:
            def new_call(self, *args, **kwargs):
                try:
                    # 获取 schedule_job
                    if schedule_job := kwargs.pop("schedule_job", None) or getattr(self, "schedule_job", None):
                        # 防止 schedule_job 被重复调用
                        setattr(self, "schedule_job", None)
                        assert isinstance(schedule_job, Job), "schedule_job 必须是 schedule.Job 类型"

                        # 添加定时任务
                        schedule_job.do(self, *args, **kwargs)

                    # 调用原始的 __call__ 方法
                    return original_call(self, *args, **kwargs)
                except Exception as e:
                    # 捕获并处理异常
                    self.handle_exception(e, name)

        # 替换原始 __call__ 方法
        dct["__call__"] = new_call

        # 创建类
        new_class = super().__new__(cls, name, bases, dct)
        return new_class


class BaseScript(metaclass=ScriptMeta):
    """脚本基类"""

    @classmethod
    def handle_exception(cls, _, class_name):
        error_stack = traceback.format_exc()
        LOG.error(error_stack)
        # 飞书通知
        cls._feishu_alarm(class_name=class_name, stack=error_stack)

    @classmethod
    def _feishu_alarm(cls, class_name, stack):
        try:
            message_dict = {
                "config": {},
                "i18n_elements": {
                    "zh_cn": [
                        {"tag": "markdown", "content": f"**🗳脚本：** {class_name}", "text_align": "left",
                         "text_size": "normal"},
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
                        "title": {"tag": "plain_text", "content": "🚨脚本异常🚨"},
                        "subtitle": {"tag": "plain_text", "content": ""},
                        "template": "blue",
                    }
                },
            }
            # 发送告警信息
            MESSAGE_FACTORY.send_alarm(message_dict)
        except Exception as e:
            LOG.exception(f"发送告警信息时发生错误: {e}")


class BaseTgScript(BaseScript):
    session_file = settings.tg.session_file
    api_id = settings.tg.api_id
    api_hash = settings.tg.api_hash
    phone = settings.tg.phone

    def __init__(self):
        self.client = TelegramClient(
            session=self.session_file,
            api_id=self.api_id,
            api_hash=self.api_hash,
            timeout=3
        )

    async def init_client(self):
        try:
            conn = self.client.start(phone=self.phone)
            if isawaitable(conn):
                await conn

            LOG.info("Client started successfully.")
            me = await self.client.get_me()
            LOG.info("User Details:")
            LOG.info(f"ID: {me.id}")
            LOG.info(f"Username: {me.username}")
            LOG.info(f"Phone: {me.phone}")

        except errors.SessionPasswordNeededError:
            LOG.error("Two-step verification is enabled. Please provide the password.")
        except errors.PhoneCodeInvalidError:
            LOG.error("The provided phone code is invalid.")
        except errors.PhoneNumberInvalidError:
            LOG.error("The provided phone number is invalid.")
        except Exception as e:
            LOG.error(f"An unexpected error occurred: {e}")

    async def shutdown(self):
        await self.client.disconnect()
        LOG.info("Client disconnected.")


class BaseDBScript(BaseScript):
    @classmethod
    async def init_db(cls):
        """初始化 Tortoise ORM"""
        await Tortoise.init(config=TORTOISE_ORM)

    @classmethod
    async def close_db(cls):
        """关闭 Tortoise ORM 连接"""
        await Tortoise.close_connections()


class TGClientMethod:
    @classmethod
    def get_client(cls, account: Account) -> TelegramClient:
        """
        获取客户端
        :param account:
        :return:
        """
        session = os.path.join(settings.tg.session_path, f"{account.phone}.session")
        return TelegramClient(
            session=session,
            api_id=account.api_id,
            api_hash=account.api_hash,
            timeout=3
        )

    @classmethod
    async def start_client(cls, client: TelegramClient, account: Account, code_callback=None):
        """
        启动客户端
        :param client:
        :param account:
        :param code_callback:
        :return:
        """
        if account.password:
            LOG.info(f"Start client with password. Account: {account.phone}")
            conn = client.start(phone=account.phone, password=account.password, code_callback=code_callback)
        else:
            LOG.info(f"Start client with code. Account: {account.phone}", code_callback=code_callback)
            conn = client.start(phone=account.phone, code_callback=code_callback)

        if isawaitable(conn):
            await conn

        LOG.info(f"Client started successfully. Account: {account.phone}")


class SIOClientMethod:
    @classmethod
    async def send_login_update_message(cls, phone: str, message: str):
        await sio.emit(SioEvent.TG_ACCOUNT_LOGIN_UPDATE.value, data=message, room=phone)

    @classmethod
    async def send_login_success(cls, phone: str):
        await sio.emit(SioEvent.TG_ACCOUNT_LOGIN_SUCCESS.value, room=phone)

    @classmethod
    async def send_login_error(cls, phone: str):
        await sio.emit(SioEvent.TG_ACCOUNT_LOGIN_ERROR.value, room=phone)

    @classmethod
    async def send_sync_dialog_info_update_message(cls, phone: str, message: str):
        await sio.emit(SioEvent.TG_ACCOUNT_DIALOG_INFO_SYNC_UPDATE.value, data=message, room=phone)

    @classmethod
    async def send_sync_dialog_info_success(cls, phone: str):
        await sio.emit(SioEvent.TG_ACCOUNT_DIALOG_INFO_SYNC_SUCCESS.value, room=phone)

    @classmethod
    async def send_sync_dialog_info_error(cls, phone: str):
        await sio.emit(SioEvent.TG_ACCOUNT_DIALOG_INFO_SYNC_ERROR.value, room=phone)


class DemoAsyncScript(BaseScript):
    schedule_job = schedule.every(1).seconds

    async def async_init(self):
        """初始化任务"""
        LOG.info(f"Async init for {self.__class__.__name__}")
        await asyncio.sleep(1)  # 模拟异步初始化

    async def __call__(self, *args, **kwargs):
        """实际任务逻辑"""
        LOG.info("异步任务开始")
        await asyncio.sleep(1)
        LOG.info("异步任务结束")


async def main():
    script = DemoAsyncScript()

    await script.async_init()

    # 异步定时任务执行
    async def run_tasks():
        await script()
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)  # 确保事件循环不会阻塞

    try:
        await run_tasks()
    except KeyboardInterrupt:
        LOG.info("Shutting down...")
    finally:
        LOG.info("Clean up and exit")


if __name__ == '__main__':
    asyncio.run(main())
