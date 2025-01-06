from tortoise import fields

from cores.constant.tg import DialogType, AccountStatus, DialogSyncType, DialogSyncStatus
from cores.model import Model


class Account(Model):
    """
    账号表
    """
    name = fields.CharField(max_length=50)
    phone = fields.CharField(max_length=20, description="手机号 +86开头")
    password = fields.CharField(max_length=50, default="", null=False)
    api_id = fields.CharField(max_length=50, default="", null=False)
    api_hash = fields.CharField(max_length=50, default="")
    status = fields.IntEnumField(enum_type=AccountStatus, default=AccountStatus.EXPIRED)
    username = fields.CharField(max_length=50, default="", null=False)
    first_name = fields.CharField(max_length=50, default="", null=False)
    last_name = fields.CharField(max_length=50, default="", null=False)
    tg_id = fields.CharField(max_length=50, default="", null=False)

    class Meta:
        table = "tg_accounts"


class Dialog(Model):
    """
    对话表
    """
    title = fields.CharField(max_length=50, null=True)
    username = fields.CharField(max_length=50, null=True)
    type = fields.IntEnumField(enum_type=DialogType, default=DialogType.USER)
    status = fields.BooleanField(default=True)
    tg_id = fields.CharField(max_length=50, null=False)
    account = fields.ForeignKeyField("models.Account", related_name="dialogs")

    class Meta:
        table = "tg_dialogs"
        indexes = [
            ("tg_id", "account_id"),
        ]


class DialogSync(Model):
    """
    对话同步表
    """
    account = fields.ForeignKeyField("models.Account", related_name="syncs")
    from_dialog = fields.ForeignKeyField("models.Dialog", related_name="from_syncs")
    to_dialog = fields.ForeignKeyField("models.Dialog", related_name="to_syncs")
    type = fields.IntEnumField(enum_type=DialogSyncType, default=DialogSyncType.AUTO)
    status = fields.IntEnumField(enum_type=DialogSyncStatus, default=DialogSyncStatus.NORMAL)

    class Meta:
        table = "tg_dialog_syncs"
        indexes = [
            ("account_id", "from_dialog_id", "to_dialog_id"),
        ]
