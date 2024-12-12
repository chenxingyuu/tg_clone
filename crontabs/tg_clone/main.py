import asyncio
from inspect import isawaitable

import schedule
from telethon import TelegramClient, errors

from cores.config import settings
from cores.log import LOG
from crontabs.base import BaseScript


class TGClone(BaseScript):
    schedule_job = schedule.every(1).seconds

    def __init__(self):
        self.api_id = settings.tg.api_id
        self.api_hash = settings.tg.api_hash
        self.phone = settings.tg.phone
        self.session_file = settings.tg.session_file

        self.client = TelegramClient(self.session_file, self.api_id, self.api_hash, timeout=3)

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
            return True

        except errors.SessionPasswordNeededError:
            LOG.error("Two-step verification is enabled. Please provide the password.")
        except errors.PhoneCodeInvalidError:
            LOG.error("The provided phone code is invalid.")
        except errors.PhoneNumberInvalidError:
            LOG.error("The provided phone number is invalid.")
        except Exception as e:
            LOG.error(f"An unexpected error occurred: {e}")
        finally:
            await self.shutdown()
            return False

    async def shutdown(self):
        await self.client.disconnect()
        LOG.info("Client disconnected.")

    async def __call__(self, *args, **kwargs):
        LOG.info("Running script...")


async def main():
    server = TGClone()
    await server.init_client()

    # 异步定时任务执行
    async def run_tasks():
        await server()
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)  # 确保事件循环不会阻塞

    try:
        await run_tasks()
    except KeyboardInterrupt:
        LOG.info("Shutting down...")
    finally:
        LOG.info("Clean up and exit")
        await server.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
