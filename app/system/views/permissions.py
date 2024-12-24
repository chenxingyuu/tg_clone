import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from app.system.filters import ListPermissionFilterSet
from app.system.models import Permission, User
from app.system.serializers.permission import (
    PermissionCreate,
    PermissionDetail,
    PermissionPatch,
    PermissionUpdate,
)
from app.system.views.auth import get_current_active_user
from cores.paginate import PageModel, PaginationParams, paginate
from cores.response import ResponseModel

permission_router = APIRouter()


@permission_router.post(
    "",
    summary="创建权限",
    response_model=ResponseModel[PermissionDetail],
    dependencies=[Security(get_current_active_user, scopes=["system:permission:create"])],
)
async def create_permission(
    permission: PermissionCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    创建一个新的权限。
    - **permission**: 要创建的权限的详细信息。
    """
    permission_obj = await Permission.create(**permission.dict(), creator_id=current_user.id)
    response = await PermissionDetail.from_tortoise_orm(permission_obj)
    return ResponseModel(data=response)


@permission_router.get(
    "",
    summary="获取权限列表",
    response_model=ResponseModel[PageModel[PermissionDetail]],
    dependencies=[Security(get_current_active_user, scopes=["system:permission:read"])],
)
async def list_permissions(
    permission_filter: ListPermissionFilterSet = Depends(),
    pagination: PaginationParams = Depends(),
):
    """
    获取所有权限的列表，可以按名称和描述进行搜索。
    """
    query = permission_filter.apply_filters()
    page_data = await paginate(query, pagination, PermissionDetail)
    return ResponseModel(data=page_data)


@permission_router.get(
    "/all",
    summary="获取所有权限列表",
    response_model=ResponseModel[List[PermissionDetail]],
    dependencies=[Security(get_current_active_user, scopes=["system:permission:read"])],
)
async def all_permissions(
    permission_filter: ListPermissionFilterSet = Depends(),
):
    """
    获取所有权限的列表，可以按名称和描述进行搜索。
    """
    query = permission_filter.apply_filters()
    permissions = await PermissionDetail.from_queryset(query)
    return ResponseModel(data=permissions)


@permission_router.get(
    "/{permission_id}",
    summary="获取权限详细信息",
    response_model=ResponseModel[PermissionDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:permission:read"])],
)
async def get_permission(permission_id: int):
    """
    根据权限 ID 获取单个权限的详细信息。
    - **permission_id**: 权限的唯一标识符。
    """
    try:
        permission = Permission.get_queryset().get(id=permission_id)
        response = await PermissionDetail.from_queryset_single(permission)
        return ResponseModel(data=response)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Permission {permission_id} not found")


@permission_router.put(
    "/{permission_id}",
    summary="更新权限信息",
    response_model=ResponseModel,
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:permission:update"])],
)
async def update_permission(permission_id: int, permission: PermissionUpdate):
    """
    更新指定 ID 权限的信息。
    - **permission_id**: 要更新的权限的唯一标识符。
    - **permission**: 更新后的权限详细信息。
    """
    permission_obj = await Permission.get_queryset().get_or_none(id=permission_id)
    if not permission_obj:
        raise HTTPException(status_code=404, detail=f"Permission {permission_id} not found")

    await Permission.get_queryset().filter(id=permission_id).update(
        **permission.dict(exclude_unset=True)
    )
    return ResponseModel()


@permission_router.patch(
    "/{permission_id}",
    summary="部分更新权限信息",
    response_model=ResponseModel,
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:permission:update"])],
)
async def patch_permission(permission_id: int, permission: PermissionPatch):
    """
    部分更新指定 ID 权限的信息。
    - **permission_id**: 要更新的权限的唯一标识符。
    - **permission**: 更新后的权限详细信息（仅更新提供的字段）。
    """
    permission_obj = await Permission.get_queryset().get_or_none(id=permission_id)
    if not permission_obj:
        raise HTTPException(status_code=404, detail=f"Permission {permission_id} not found")

    await Permission.get_queryset().filter(id=permission_id).update(
        **permission.dict(exclude_unset=True)
    )
    return ResponseModel()


@permission_router.delete(
    "/{permission_id}",
    summary="删除权限",
    response_model=ResponseModel,
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:permission:delete"])],
)
async def delete_permission(permission_id: int):
    """
    逻辑删除指定 ID 的权限。
    - **permission_id**: 要删除的权限的唯一标识符。
    """
    try:
        permission = await Permission.get_queryset().get(id=permission_id)
        permission.deleted_at = datetime.datetime.now()
        await permission.save()
        return ResponseModel()
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Permission {permission_id} not found")
