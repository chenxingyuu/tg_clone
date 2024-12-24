import logging

from tortoise import Tortoise, fields, models
from tortoise.queryset import QuerySet

from cores.config import settings
from cores.log import LOG

LOG.level("debug", no=10, color="<blue>")
LOG.level("info", no=20, color="<white>")
LOG.level("warning", no=30, color="<yellow>")
LOG.level("error", no=40, color="<red>")


# 替换 logging 模块的 handler
class InterceptHandler(logging.Handler):
    def emit(self, record):
        loguru_level = record.levelname.lower()
        if loguru_level == "warn":
            loguru_level = "warning"
        logger_opt = LOG.opt(depth=6, exception=record.exc_info)
        logger_opt.log(loguru_level, record.getMessage())


# 将 tortoise 的日志交给 loguru
logging.basicConfig(handlers=[InterceptHandler()], level=logging.DEBUG)


class SoftDeleteQuerySet(QuerySet):
    def active(self):
        return self.filter(deleted_at=None)


class Model(models.Model):
    id = fields.IntField(pk=True)
    creator_id = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(default=None, null=True)

    class Meta:
        abstract = True

    @classmethod
    def get_queryset(cls):
        return SoftDeleteQuerySet(cls).active()


TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": settings.mysql.host,
                "port": settings.mysql.port,
                "user": settings.mysql.user,
                "password": settings.mysql.password,
                "database": settings.mysql.database,
                "maxsize": 10,  # 最大连接数
                "minsize": 1,  # 最小连接数
                "connect_timeout": 15,  # 连接超时时间
                "charset": "utf8mb4",
            },
        }},
    "apps": {
        "models": {
            "models": [
                "app.system.models",
                "app.tg.models",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
}


async def init_db():
    LOG.info("Initializing database...")
    await Tortoise.init(config=TORTOISE_ORM)


async def close_db():
    LOG.info("Closing database...")
    await Tortoise.close_connections()
