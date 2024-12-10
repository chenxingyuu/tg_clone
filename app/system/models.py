from tortoise import fields

from cores.model import Model


class User(Model):
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=50, unique=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    roles = fields.ManyToManyField("models.Role", related_name="users", through="system_user_roles")

    class Meta:
        table = "system_users"


class Role(Model):
    name = fields.CharField(max_length=50, unique=True)
    description = fields.TextField(null=True)
    permissions = fields.ManyToManyField(
        "models.Permission",
        related_name="roles",
        through="system_role_permissions",
    )
    menus = fields.ManyToManyField("models.Menu", related_name="roles", through="system_role_menus")

    class Meta:
        table = "system_roles"


class Permission(Model):
    name = fields.CharField(max_length=100, unique=True)
    description = fields.TextField(null=True)

    class Meta:
        table = "system_permissions"


class Menu(Model):
    name = fields.CharField(max_length=50, unique=True)
    path = fields.CharField(max_length=50, unique=True)
    components = fields.CharField(max_length=50)
    meta_locale = fields.CharField(max_length=50, null=True)
    meta_icon = fields.CharField(max_length=50, null=True)
    meta_requires_auth = fields.BooleanField(default=False)
    meta_order = fields.IntField(default=0)
    meta_hide_in_menu = fields.BooleanField(default=False)
    meta_hide_children_in_menu = fields.BooleanField(default=False)
    meta_no_affix = fields.BooleanField(default=False)
    meta_ignore_cache = fields.BooleanField(default=False)
    parent = fields.ForeignKeyField("models.Menu", on_delete=fields.CASCADE, null=True)

    class Meta:
        table = "system_menus"
