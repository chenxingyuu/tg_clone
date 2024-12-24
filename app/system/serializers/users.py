from tortoise.contrib.pydantic import pydantic_model_creator

from app.system.models import User

UserDetail = pydantic_model_creator(
    User,
    name="UserDetail",
    include=(
        "id",
        "username",
        "email",
        "is_active",
        "created_at",
    ),
)

UserCreate = pydantic_model_creator(User, name="UserCreate", include=("username", "email"))

UserUpdate = pydantic_model_creator(
    User,
    name="UserUpdate",
    include=("username", "email", "is_active"),
)

UserPatch = pydantic_model_creator(
    User,
    name="UserPatch",
    include=("username", "email", "is_active"),
)
