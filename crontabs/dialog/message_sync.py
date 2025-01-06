import asyncio
from typing import List

from telethon.tl.types import MessageService

from app.tg.models import DialogSync
from cores.constant.tg import DialogSyncSetting
from cores.log import LOG
from crontabs.base import TGClientMethod, BaseDBScript, SIOClientMethod


class DialogMessageSync(BaseDBScript, TGClientMethod, SIOClientMethod):
    def __init__(self):
        pass

    @classmethod
    async def get_dialog_sync_tasks(cls) -> List[DialogSync]:
        return await DialogSync.get_queryset().select_related('account', 'from_dialog', 'to_dialog').filter(status=1).all()

    async def sync_dialog_message(self, account, from_dialog, to_dialog, settings):
        # 初始化TG客户端
        client = self.get_client(account)
        await self.start_client(client=client, account=account)
        # 获取对话实体
        from_dialog_entity = await client.get_entity(from_dialog.tg_id)
        to_dialog_entity = await client.get_entity(to_dialog.tg_id)
        # 获取对话消息
        async for message in client.iter_messages(from_dialog_entity, reverse=settings.message_reversed):
            LOG.info(f"Message: {message.to_dict()}")
            # 跳过系统消息
            if isinstance(message, MessageService):
                continue
            # 发送消息
            await client.send_message(to_dialog_entity, message)

    async def __call__(self):
        tasks = await self.get_dialog_sync_tasks()
        LOG.info(f"Dialog sync tasks: {tasks}")

        # 每个任务启动一个协程
        futures = []
        for task in tasks:
            LOG.info(f"Syncing dialog: {task.account.name} {task.from_dialog.title} -> {task.to_dialog.title}")
            settings = DialogSyncSetting(**task.settings)
            future = self.sync_dialog_message(task.account, task.from_dialog, task.to_dialog, settings)
            futures.append(future)
        await asyncio.gather(*futures)


async def main():
    script = DialogMessageSync()

    await script.init_db()

    await script()

    await script.close_db()


if __name__ == '__main__':
    asyncio.run(main())
