import asyncio

from cores.log import LOG
from crontabs.base import BaseTgScript


class ChannelList(BaseTgScript):
    def __init__(self):
        super().__init__()

    async def __call__(self, *args, **kwargs):
        # 列出所有频道
        async for dialog in self.client.iter_dialogs():
            LOG.info(f"{dialog.id} {dialog.title}")


async def main():
    server = ChannelList()
    await server.init_client()
    await server()
    await server.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
