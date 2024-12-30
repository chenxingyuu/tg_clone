from typing import List

from fastapi import Security, APIRouter, Depends, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.functions import Count

from app.system.views.auth import get_current_active_user
from app.tg.filters import ListAccountFilterSet
from app.tg.models import Account
from app.tg.serializers.account import AccountDetail, AccountCreate, AccountPatch, AccountDetailPagination
from cores.paginate import PageModel, PaginationParams, paginate
from cores.response import ResponseModel

account_router = APIRouter()


@account_router.post(
    "",
    summary="创建TG账户",
    response_model=ResponseModel[AccountDetail],
    dependencies=[Security(get_current_active_user, scopes=["tg:account:create"])],
)
async def create_account(account: AccountCreate):
    """
    创建一个新的TG账户。
    - **account**: 要创建的TG账户的详细信息。
    """
    account_obj = await Account.create(**account.dict())
    response = await AccountDetail.from_tortoise_orm(account_obj)
    return ResponseModel(data=response)


@account_router.get(
    "",
    summary="获取TG账户列表",
    response_model=ResponseModel[PageModel[AccountDetailPagination]],
    dependencies=[Security(get_current_active_user, scopes=["tg:account:read"])],
)
async def list_accounts(
    account_filter: ListAccountFilterSet = Depends(),
    pagination: PaginationParams = Depends(),
):
    """
    获取所有TG账户的列表。
    """
    query = account_filter.apply_filters().annotate(dialog_count=Count("channels"))
    page_data = await paginate(query, pagination, AccountDetailPagination)
    return ResponseModel(data=page_data)


@account_router.get(
    "/all",
    summary="获取全部TG账户列表",
    response_model=ResponseModel[List[AccountDetail]],
    dependencies=[Security(get_current_active_user, scopes=["tg:account:read"])],
)
async def list_accounts_all(
    account_filter: ListAccountFilterSet = Depends(),
):
    """
    获取所有TG账户的列表。
    """
    query = account_filter.apply_filters()
    account_data = await AccountDetail.from_queryset(query)
    return ResponseModel(data=account_data)


@account_router.patch(
    "/{account_id}",
    summary="部分更新账号信息",
    response_model=ResponseModel[AccountDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["tg:account:update"])],
)
async def patch_account(account_id: int, account: AccountPatch):
    """
    部分更新指定 ID 账号的信息。
    - **account_id**: 要更新的账号的唯一标识符。
    - **account**: 更新后的账号详细信息（仅更新提供的字段）。
    """
    account_obj = await Account.get_queryset().get_or_none(id=account_id)
    if not account_obj:
        raise HTTPException(status_code=404, detail=f"account {account_id} not found")

    await Account.get_queryset().filter(id=account_id).update(**account.dict(exclude_unset=True))
    updated_account = Account.get_queryset().get(id=account_id)
    response = await AccountDetail.from_queryset_single(updated_account)
    return ResponseModel(data=response)
