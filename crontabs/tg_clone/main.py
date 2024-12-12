import asyncio

import schedule
from telethon.tl.types import InputMessagesFilterVideo

from cores.config import settings
from cores.log import LOG
from crontabs.base import BaseTgScript


class TGClone(BaseTgScript):
    schedule_job = schedule.every(1).seconds

    async def __call__(self, *args, **kwargs):
        LOG.info("Running script...")
        # 查询 id 为 -1002210339889 的 chanel
        channel = await self.client.get_entity(-1002210339889)
        LOG.info(f"Channel: {channel.title}")
        # 下载频道的所有文件
        async for message in self.client.iter_messages(channel, reverse=True, filter=InputMessagesFilterVideo):
            LOG.info(f"Message: {message.id} {message.text}")
            if message.media:
                await self.client.download_media(message.media, file=f"{settings.tg.file_save_path}/{message.id}")


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
