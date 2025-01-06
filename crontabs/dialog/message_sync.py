import asyncio
from typing import List

from app.tg.models import DialogSync
from cores.log import LOG
from crontabs.base import TGClientMethod, BaseDBScript, SIOClientMethod


class DialogMessageSync(BaseDBScript, TGClientMethod, SIOClientMethod):
    def __init__(self):
        pass

    @classmethod
    async def get_dialog_sync_tasks(cls) -> List[DialogSync]:
        return await DialogSync.get_queryset().select_related('account', 'from_dialog', 'to_dialog').filter(status=1).all()

    async def sync_dialog_message(self, account, from_dialog, to_dialog):
        # 初始化TG客户端
        client = self.get_client(account)
        from_dialog_entity = await client.get_entity(from_dialog.id)
        to_dialog_entity = await client.get_entity(to_dialog.id)

        # 获取对话消息
        async for message in client.iter_messages(from_dialog_entity):
            # 发送消息
            LOG.info(f"Sending message: {message}")
            await client.send_message(to_dialog_entity, message)

    async def __call__(self):
        tasks = await self.get_dialog_sync_tasks()
        LOG.info(f"Dialog sync tasks: {tasks}")

        for task in tasks:
            LOG.info(f"Syncing dialog: {task.account.name} {task.from_dialog.title} -> {task.to_dialog.title}")
            await self.sync_dialog_message(task.account, task.from_dialog, task.to_dialog)


async def main():
    script = DialogMessageSync()

    await script.init_db()

    await script()

    await script.close_db()


if __name__ == '__main__':
    asyncio.run(main())
