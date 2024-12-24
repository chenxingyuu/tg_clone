from typing import List

from fastapi import APIRouter, HTTPException, Security
from tortoise.contrib.fastapi import HTTPNotFoundError

from app.system.models import Menu, Role
from app.system.serializers.menus import MenuDetail
from app.system.serializers.roles import RoleDetail
from app.system.views.auth import get_current_active_user
from cores.response import ResponseModel

role_menu_router = APIRouter()


@role_menu_router.get(
    "/{role_id}/menus",
    summary="角色的菜单列表",
    response_model=ResponseModel[List[MenuDetail]],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:role:read", "system:permission:read"],
        )
    ],
)
async def get_role_menus(role_id: int):
    """
    根据角色 ID 获取单个角色的菜单列表。
    - **role_id**: 角色的唯一标识符。
    """
    role = await Role.get_queryset().prefetch_related("menus").get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    menus_data = await MenuDetail.from_queryset(role.menus.all())
    return ResponseModel(data=menus_data)


@role_menu_router.post(
    "/{role_id}/menus",
    summary="为角色添加菜单",
    response_model=ResponseModel[RoleDetail],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:role:update", "system:permission:read"],
        )
    ],
)
async def add_permission_to_role(role_id: int, permission_ids: List[int]):
    """
    为角色添加一个或多个菜单。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要添加的菜单的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    menus = await Menu.get_queryset().filter(id__in=permission_ids).all()
    if len(menus) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in menus}
        raise HTTPException(
            status_code=404,
            detail=f"Menus with IDs {missing_ids} not found",
        )
    menus_need_add = [menu for menu in menus if menu not in role.menus]
    await role.menus.add(*menus_need_add)
    return ResponseModel()


@role_menu_router.delete(
    "/{role_id}/menus",
    summary="删除角色菜单",
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
    删除角色的一个或多个菜单。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要删除的菜单的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    menus = await Menu.get_queryset().filter(id__in=permission_ids).all()
    if len(menus) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in menus}
        raise HTTPException(
            status_code=404,
            detail=f"Menus with IDs {missing_ids} not found",
        )

    await role.menus.remove(*menus)
    return ResponseModel()


@role_menu_router.put(
    "/{role_id}/menus",
    summary="修改角色菜单",
    response_model=ResponseModel,
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:role:update", "system:permission:read"],
        )
    ],
)
async def update_menus_for_role(role_id: int, permission_ids: List[int]):
    """
    修改角色的菜单（覆盖更新）。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要设置的菜单的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    menus = await Menu.get_queryset().filter(id__in=permission_ids).all()
    if len(menus) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in menus}
        raise HTTPException(
            status_code=404,
            detail=f"Menus with IDs {missing_ids} not found",
        )

    await role.menus.clear()
    await role.menus.add(*menus)
    return ResponseModel()
