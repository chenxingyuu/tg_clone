from tortoise.contrib.pydantic import pydantic_model_creator

from app.system.models import User

UserDetail = pydantic_model_creator(
    User,
    name="UserDetail",
    include=(
        "id",
        "username",
        "is_active",
        "is_superuser",
        "created_at",
        "updated_at",
        "deleted_at",
        "creator_id",
    ),
)

UserCreate = pydantic_model_creator(User, name="UserCreate", include=("username",))

UserUpdate = pydantic_model_creator(
    User,
    name="UserUpdate",
    include=("username", "is_active"),
)
UserPatch = pydantic_model_creator(
    User,
    name="UserPatch",
    include=("username", "is_active"),
)
