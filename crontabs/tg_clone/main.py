import os

from dotenv import load_dotenv
from telethon import TelegramClient

from cores.log import LOG

# 加载配置
load_dotenv()
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')

# 创建 Telegram 客户端
client = TelegramClient('session_name', api_id, api_hash, timeout=3)


async def main():
    # 获取当前登录用户的信息
    me = await client.get_me()

    LOG.info("User Details:")
    LOG.info(f"ID: {me.id}")
    LOG.info(f"Username: {me.username}")
    LOG.info(f"Phone: {me.phone}")
    LOG.info(f"First Name: {me.first_name}")
    LOG.info(f"Last Name: {me.last_name}")

    # 获取最近对话
    LOG.info("Recent Dialogs:")
    async for dialog in client.iter_dialogs(limit=10):  # 获取最近 10 个会话
        LOG.info(f"{dialog.name} ({dialog.entity.id})")


# 运行客户端
with client.start(phone=os.getenv('PHONE')) as client:
    client.loop.run_until_complete(main())
