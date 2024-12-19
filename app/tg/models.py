from tortoise import fields

from cores.model import Model


class Account(Model):
    """
    账号表
    """
    name = fields.CharField(max_length=50)
    phone = fields.CharField(max_length=20, description="手机号 +86开头")
    api_id = fields.CharField(max_length=50, default="", null=False)
    api_hash = fields.CharField(max_length=50, default="")
    status = fields.BooleanField(default=True)
    username = fields.CharField(max_length=50, default="", null=False)
    first_name = fields.CharField(max_length=50, default="", null=False)
    last_name = fields.CharField(max_length=50, default="", null=False)
    tg_id = fields.CharField(max_length=50, default="", null=False)

    class Meta:
        table = "tg_accounts"
