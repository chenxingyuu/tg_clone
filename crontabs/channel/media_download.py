import asyncio

import schedule

from cores.log import LOG
from crontabs.base import BaseTgScript


class ChannelMediaDownload(BaseTgScript):
    schedule_job = schedule.every(10000).seconds

    def __init__(self):
        super().__init__()

    async def __call__(self, *args, **kwargs):
        LOG.info("Running ChannelMediaDownload Script...")
        # 查询 id 为 -1002210339889 的 channel
        channel = await self.client.get_entity(-1002210339889)
        # 遍历频道的所有文件，过滤出包含 media 的消息
        async for message in self.client.iter_messages(channel, reverse=True, filter=lambda m: m.media):
            LOG.info(f"Message: {message.text}")


async def main():
    server = ChannelMediaDownload()
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
