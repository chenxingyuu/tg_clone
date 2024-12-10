from tortoise.contrib.pydantic import pydantic_model_creator

from app.system.models import Role

RoleDetail = pydantic_model_creator(
    Role,
    name="RoleDetail",
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
RoleCreate = pydantic_model_creator(Role, name="RoleCreate", include=("name", "description"))
RoleUpdate = RoleCreate
RolePatch = RoleCreate
