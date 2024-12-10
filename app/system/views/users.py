from fastapi import APIRouter, Depends, HTTPException, Security
from tortoise.contrib.fastapi import HTTPNotFoundError

from app.system.filters import ListUserFilterSet
from app.system.models import User
from app.system.serializers.users import UserCreate, UserDetail, UserPatch, UserUpdate
from app.system.views.auth import get_current_active_user
from cores.paginate import PageModel, PaginationParams, paginate
from cores.pwd import get_password_hash
from cores.response import ResponseModel

user_router = APIRouter()


async def validate_user(user_id: int) -> User:
    if not (user := await User.get_queryset().get_or_none(id=user_id)):
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


@user_router.post(
    path="",
    summary="创建用户",
    response_model=ResponseModel[UserDetail],
    dependencies=[Security(get_current_active_user, scopes=["system:user:create"])],
)
async def create_user(user: UserCreate):
    """
    创建一个新的系统用户。
    - **user**: 要创建的用户的详细信息。
    """
    password = f"{user.username}@123456"
    hashed_password = get_password_hash(password)
    user_obj = await User.create(**user.dict(exclude_unset=True), hashed_password=hashed_password)
    user_data = await UserDetail.from_tortoise_orm(user_obj)
    return ResponseModel(data=user_data)


@user_router.get(
    "",
    summary="获取用户列表",
    response_model=ResponseModel[PageModel[UserDetail]],
    dependencies=[Security(get_current_active_user, scopes=["system:user:read"])],
)
async def list_user(
    user_filter: ListUserFilterSet = Depends(),
    pagination: PaginationParams = Depends(),
):
    """
    获取系统用户列表，支持多种过滤条件。
    - **username**: 用户名过滤条件（模糊匹配）。
    - **email**: 电子邮件过滤条件（模糊匹配）。
    - **is_active**: 是否激活过滤条件。
    - **is_superuser**: 是否超级用户过滤条件。
    """
    query = user_filter.apply_filters()
    page_data = await paginate(query, pagination, UserDetail)
    return ResponseModel(data=page_data)


@user_router.get(
    "/{user_id}",
    summary="获取用户详细信息",
    response_model=ResponseModel[UserDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:user:read"])],
)
async def get_user(user_id: int):
    """
    根据用户 ID 获取单个用户的详细信息。
    - **user_id**: 用户的唯一标识符。
    """
    user = await User.get_queryset().get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    user_data = await UserDetail.from_tortoise_orm(user)
    return ResponseModel(data=user_data)


@user_router.put(
    "/{user_id}",
    summary="更新用户信息",
    response_model=ResponseModel[UserDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:user:update"])],
)
async def update_user(user_id: int, user: UserUpdate):
    """
    更新指定 ID 用户的信息。
    - **user_id**: 要更新的用户的唯一标识符。
    - **user**: 更新后的用户详细信息。
    """
    user_obj = await User.get_queryset().get(id=user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    await User.get_queryset().filter(id=user_id).update(**user.dict(exclude_unset=True))

    user_data = await UserDetail.from_tortoise_orm(user_obj)
    return ResponseModel(data=user_data)


@user_router.patch(
    "/{user_id}",
    summary="部分更新用户信息",
    response_model=ResponseModel[UserDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:user:update"])],
)
async def patch_user(user_id: int, user: UserPatch):
    """
    部分更新指定 ID 用户的信息。
    - **user_id**: 要更新的用户的唯一标识符。
    - **user**: 更新后的用户详细信息（仅更新提供的字段）。
    """
    updated_count = (
        await User.get_queryset().filter(id=user_id).update(**user.dict(exclude_unset=True))
    )
    if not updated_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    user_obj = await User.get_queryset().get(id=user_id)
    user_data = await UserDetail.from_tortoise_orm(user_obj)
    return ResponseModel(data=user_data)


@user_router.delete(
    "/{user_id}",
    summary="删除用户",
    response_model=ResponseModel[dict],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:user:delete"])],
)
async def delete_user(user_id: int):
    """
    删除指定 ID 的用户。
    - **user_id**: 要删除的用户的唯一标识符。
    """
    deleted_count = await User.get_queryset().filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return ResponseModel(data={"deleted": deleted_count})
