from typing import List

from fastapi import APIRouter, Depends, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError

from app.system.models import Menu, User
from app.system.serializers.menus import MenuDetailTree
from app.system.serializers.users import UserDetail, UserUpdate
from app.system.views.auth import get_current_active_user
from cores.response import ResponseModel
from cores.scope import filter_scopes

user_me_router = APIRouter()


@user_me_router.get(
    "/me",
    summary="获取我的详细信息",
    response_model=ResponseModel[UserDetail],
)
async def get_user_me(current_user: User = Depends(get_current_active_user)):
    user_data = UserDetail.from_orm(current_user)
    return ResponseModel(data=user_data)


@user_me_router.put(
    "/me",
    summary="更新我的详细信息",
    response_model=ResponseModel[UserDetail],
)
async def update_user_me(user: UserUpdate, current_user: User = Depends(get_current_active_user)):
    updated_count = (
        await User.get_queryset().filter(id=current_user.id).update(**user.dict(exclude_unset=True))
    )
    if not updated_count:
        raise HTTPException(status_code=404, detail=f"User {current_user.id} not found")
    user_obj = await User.get_queryset().get(id=current_user.id)
    user_data = await UserDetail.from_tortoise_orm(user_obj)
    return ResponseModel(data=user_data)


@user_me_router.delete(
    "/me",
    summary="删除自己的账号",
    response_model=ResponseModel[dict],
    responses={404: {"model": HTTPNotFoundError}},
)
async def delete_user_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    删除指定 ID 的用户。
    - **user_id**: 要删除的用户的唯一标识符。
    """
    deleted_count = await User.get_queryset().filter(id=current_user.id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {current_user.id} not found")
    return ResponseModel(data={"deleted": deleted_count})


@user_me_router.get(
    "/me/roles",
    summary="获取我的角色",
    response_model=ResponseModel[List[str]],
)
async def get_user_me_roles(
    current_user: User = Depends(get_current_active_user),
):
    # 查询用户并预加载关联的角色和权限
    user = await User.filter(id=current_user.id).prefetch_related("roles").first()
    # 从所有角色中获取权限
    roles = [role.name for role in user.roles]
    return ResponseModel(data=roles)


@user_me_router.get(
    "/me/permissions",
    summary="获取我的权限",
    response_model=ResponseModel[List[str]],
)
async def get_user_me_permissions(
    current_user: User = Depends(get_current_active_user),
):
    # 查询用户并预加载关联的权限
    user = await User.filter(id=current_user.id).prefetch_related("roles__permissions").first()

    if not user:
        return []

    # 从所有角色中获取权限
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.name)

    filter_permissions = filter_scopes(permissions)

    return ResponseModel(data=filter_permissions)


@user_me_router.get(
    "/me/menus",
    summary="获取我的菜单",
    response_model=ResponseModel[List[MenuDetailTree]],
)
async def get_user_me_menus(
    current_user: User = Depends(get_current_active_user),
):
    menus = await Menu.get_queryset().filter(roles__users__id=current_user.id)
    tree = MenuDetailTree.from_menu_list(menus=menus)
    return ResponseModel(data=tree)
