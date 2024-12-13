import asyncio

import schedule

from cores.log import LOG
from crontabs.base import BaseTgScript


class ChannelMedisSend(BaseTgScript):
    schedule_job = schedule.every(10000).days

    def __init__(self):
        super().__init__()

    async def __call__(self, *args, **kwargs):
        LOG.info("Running ChannelMedisSend Script...")
        # 查询 id 为 -1002210339889 的 channel
        channel = await self.client.get_entity(-1002435566667)
        # 往频道发送消息
        await self.client.send_message(channel, "Hello, World!")
        # 发送文件
        await self.client.send_file(channel, "README.md")
        # 发送大文件
        await self.client.send_file(channel, "README.md", force_document=True)


async def main():
    server = ChannelMedisSend()
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
