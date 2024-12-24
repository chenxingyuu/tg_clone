from typing import List

from fastapi import APIRouter, HTTPException, Security
from tortoise.contrib.fastapi import HTTPNotFoundError

from app.system.models import Permission, Role
from app.system.serializers.permission import PermissionDetail
from app.system.views.auth import get_current_active_user
from cores.response import ResponseModel

role_permission_router = APIRouter()


@role_permission_router.get(
    "/{role_id}/permissions",
    summary="角色的权限列表",
    response_model=ResponseModel[List[PermissionDetail]],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:role:read", "system:permission:read"],
        )
    ],
)
async def get_role_permissions(role_id: int):
    """
    根据角色 ID 获取单个角色的权限列表。
    - **role_id**: 角色的唯一标识符。
    """
    role = await Role.get_queryset().prefetch_related("permissions").get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    permissions_data = await PermissionDetail.from_queryset(role.permissions.all())
    return ResponseModel(data=permissions_data)


@role_permission_router.post(
    "/{role_id}/permissions",
    summary="为角色添加权限",
    response_model=ResponseModel,
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:role:update", "system:permission:read"],
        )
    ],
)
async def add_permission_to_role(role_id: int, permission_ids: List[int]):
    """
    为角色添加一个或多个权限。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要添加的权限的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    permissions = await Permission.get_queryset().filter(id__in=permission_ids).all()
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in permissions}
        raise HTTPException(
            status_code=404,
            detail=f"Permissions with IDs {missing_ids} not found",
        )
    permissions_need_add = [permission for permission in permissions if permission not in role.permissions]
    await role.permissions.add(*permissions_need_add)
    return ResponseModel()


@role_permission_router.delete(
    "/{role_id}/permissions",
    summary="删除角色权限",
    response_model=ResponseModel,
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:role:update", "system:permission:read"],
        )
    ],
)
async def delete_permission_from_role(role_id: int, permission_ids: List[int]):
    """
    删除角色的一个或多个权限。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要删除的权限的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    permissions = await Permission.get_queryset().filter(id__in=permission_ids).all()
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in permissions}
        raise HTTPException(
            status_code=404,
            detail=f"Permissions with IDs {missing_ids} not found",
        )

    await role.permissions.remove(*permissions)
    return ResponseModel()


@role_permission_router.put(
    "/{role_id}/permissions",
    summary="修改角色权限",
    response_model=ResponseModel,
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:role:update", "system:permission:read"],
        )
    ],
)
async def update_permissions_for_role(role_id: int, permission_ids: List[int]):
    """
    修改角色的权限（覆盖更新）。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要设置的权限的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    permissions = await Permission.get_queryset().filter(id__in=permission_ids).all()
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in permissions}
        raise HTTPException(
            status_code=404,
            detail=f"Permissions with IDs {missing_ids} not found",
        )

    await role.permissions.clear()
    await role.permissions.add(*permissions)
    return ResponseModel()
