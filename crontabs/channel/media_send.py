import asyncio

import schedule

from cores.log import LOG
from crontabs.base import BaseTgScript


def progress_callback(current, total):
    """进度条回调函数"""
    # 自动转换单位
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    total_unit, current_unit = 0, 0
    while total > 1024:
        total /= 1024
        total_unit += 1
    while current > 1024:
        current /= 1024
        current_unit += 1
    LOG.info(f"Uploaded {current:.2f} {units[current_unit]}/{total:.2f} {units[total_unit]} ")


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
        # 发送视频文件，显示进度条
        await self.client.send_file(
            channel,
            file="/app/data/3.mp4",
            progress_callback=progress_callback,
            background=True,
            supports_streaming=True
        )
        LOG.info("Send message and file to channel.")


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
