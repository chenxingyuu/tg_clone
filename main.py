import os

from dotenv import load_dotenv
from telethon import TelegramClient

# 加载配置
load_dotenv()
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')

# 创建 Telegram 客户端
client = TelegramClient('session_name', api_id, api_hash, timeout=3)


async def main():
    # 获取当前登录用户的信息
    me = await client.get_me()

    print("User Details:")
    print(f"ID: {me.id}")
    print(f"Username: {me.username}")
    print(f"Phone: {me.phone}")
    print(f"First Name: {me.first_name}")
    print(f"Last Name: {me.last_name}")

    # 获取最近对话
    print("\nRecent Dialogs:")
    async for dialog in client.iter_dialogs(limit=10):  # 获取最近 10 个会话
        print(f"{dialog.name} ({dialog.entity.id})")


# 运行客户端
with client:
    client.loop.run_until_complete(main())
