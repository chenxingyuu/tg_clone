from typing import List

from fastapi import APIRouter, HTTPException, Security

from app.system.models import Role, User
from app.system.serializers.roles import RoleDetail
from app.system.views.auth import get_current_active_user
from app.system.views.users import validate_user
from cores.response import ResponseModel

user_role_route = APIRouter()


# 获取用户的角色列表
@user_role_route.get(
    "/{user_id}/roles",
    summary="获取用户角色列表",
    response_model=ResponseModel[List[RoleDetail]],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:read", "system:role:read"],
        )
    ],
)
async def get_user_roles(user_id: int):
    """
    获取指定用户的角色列表。
    - **user_id**: 用户的唯一标识符。
    """
    user = await User.get_queryset().prefetch_related("roles").get_or_none(id=user_id)
    if not user:
        return ResponseModel(data=[])

    roles_data = [RoleDetail.from_orm(role) for role in user.roles]
    return ResponseModel(data=roles_data)


# 用户添加角色
@user_role_route.post(
    "/{user_id}/roles",
    summary="为用户添加角色",
    response_model=ResponseModel,
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:update", "system:role:read"],
        )
    ],
)
async def add_role_to_user(user_id: int, role_ids: List[int]):
    """
    为用户添加一个或多个角色。
    - **user_id**: 用户的唯一标识符。
    - **role_ids**: 要添加的角色的唯一标识符列表。
    """
    user = await validate_user(user_id)

    roles = await Role.get_queryset().filter(id__in=role_ids).all()
    if len(roles) != len(role_ids):
        missing_ids = set(role_ids) - {role.id for role in roles}
        raise HTTPException(
            status_code=404,
            detail=f"Roles with IDs {missing_ids} not found",
        )

    await user.roles.add(*roles)
    return ResponseModel()


# 用户修改角色
@user_role_route.put(
    "/{user_id}/roles",
    summary="修改用户角色",
    response_model=ResponseModel,
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:update", "system:role:read"],
        )
    ],
)
async def update_roles_for_user(user_id: int, role_ids: List[int]):
    """
    修改用户的角色（覆盖更新）。
    - **user_id**: 用户的唯一标识符。
    - **role_ids**: 要设置的角色的唯一标识符列表。
    """
    user = await validate_user(user_id)

    roles = await Role.get_queryset().filter(id__in=role_ids).all()
    if len(roles) != len(role_ids):
        missing_ids = set(role_ids) - {role.id for role in roles}
        raise HTTPException(
            status_code=404,
            detail=f"Roles with IDs {missing_ids} not found",
        )

    await user.roles.clear()
    await user.roles.add(*roles)

    return ResponseModel()


# 用户删除角色
@user_role_route.delete(
    "/{user_id}/roles",
    summary="删除用户角色",
    response_model=ResponseModel,
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:update", "system:role:read"],
        )
    ],
)
async def delete_roles_from_user(user_id: int, role_ids: List[int]):
    """
    删除用户的一个或多个角色。
    - **user_id**: 用户的唯一标识符。
    - **role_ids**: 要删除的角色的唯一标识符列表。
    """
    user = await validate_user(user_id)

    roles = await Role.get_queryset().filter(id__in=role_ids).all()
    if len(roles) != len(role_ids):
        missing_ids = set(role_ids) - {role.id for role in roles}
        raise HTTPException(
            status_code=404,
            detail=f"Roles with IDs {missing_ids} not found",
        )

    await user.roles.remove(*roles)

    return ResponseModel()
