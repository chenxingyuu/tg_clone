from tortoise import fields

from cores.model import Model


class Account(Model):
    """
    账号表
    """
    name = fields.CharField(max_length=50)
    phone = fields.CharField(max_length=20)
    password = fields.CharField(max_length=50)
    api_id = fields.CharField(max_length=50)
    api_hash = fields.CharField(max_length=50)
    status = fields.BooleanField(default=True)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    tg_id = fields.CharField(max_length=50)

    class Meta:
        table = "tg_accounts"
