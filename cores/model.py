from tortoise import Tortoise, fields, models
from tortoise.queryset import QuerySet

from cores.config import settings


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
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
}


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)


async def close_db():
    await Tortoise.close_connections()
