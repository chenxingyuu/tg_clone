from tortoise.contrib.pydantic import pydantic_model_creator

from app.system.models import Permission

PermissionDetail = pydantic_model_creator(
    Permission,
    name="PermissionDetail",
    include=(
        "id",
        "name",
        "description",
        "created_at",
        "updated_at",
        "deleted_at",
        "creator_id",
    ),
)
PermissionCreate = pydantic_model_creator(
    Permission, name="PermissionCreate", include=("name", "description")
)
PermissionUpdate = PermissionCreate
PermissionPatch = PermissionCreate
