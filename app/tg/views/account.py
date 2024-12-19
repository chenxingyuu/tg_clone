from fastapi import Security, APIRouter, Depends

from app.system.views.auth import get_current_active_user
from app.tg.filters import ListAccountFilterSet
from app.tg.models import Account
from app.tg.serializers.account import AccountDetail, AccountCreate
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
    response_model=ResponseModel[PageModel[AccountDetail]],
    dependencies=[Security(get_current_active_user, scopes=["tg:account:read"])],
)
async def list_accounts(
    account_filter: ListAccountFilterSet = Depends(),
    pagination: PaginationParams = Depends(),
):
    """
    获取所有TG账户的列表。
    """
    query = account_filter.apply_filters()
    page_data = await paginate(query, pagination, AccountDetail)
    return ResponseModel(data=page_data)
