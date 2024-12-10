from typing import List

from fastapi import APIRouter, Security

from app.system.models import User
from app.system.serializers.permission import PermissionDetail
from app.system.views.auth import get_current_active_user
from cores.response import ResponseModel

user_permission_route = APIRouter()


# 获取用户的权限列表
@user_permission_route.get(
    "/{user_id}/permissions",
    summary="获取用户权限列表",
    response_model=ResponseModel[List[PermissionDetail]],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:read", "system:permission:read"],
        )
    ],
)
async def get_user_permissions(user_id: int):
    """
    获取指定用户的权限列表。
    - **user_id**: 用户的唯一标识符。
    """
    # 查询用户并预加载关联的角色
    user = await User.get_queryset().prefetch_related("roles__permissions").get_or_none(id=user_id)
    if not user:
        return ResponseModel(data=[])

    # 直接从预加载的数据中获取权限，避免重复I/O操作
    permissions = set()
    for role in user.roles:
        permissions.update(role.permissions)

    # 将权限对象转换为 PermissionDetail 响应模型
    permissions_list = [PermissionDetail.from_orm(permission) for permission in permissions]

    return ResponseModel(data=permissions_list)
