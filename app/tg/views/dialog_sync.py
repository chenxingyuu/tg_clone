from fastapi import Security, APIRouter, Depends

from app.system.views.auth import get_current_active_user
from app.tg.filters import ListDialogSyncFilterSet
from app.tg.models import DialogSync
from app.tg.serializers.dialog_sync import DialogSyncDetail, DialogSyncCreate
from cores.paginate import PageModel, PaginationParams, paginate
from cores.response import ResponseModel

dialog_sync_router = APIRouter()


@dialog_sync_router.post(
    "",
    summary="创建TG账户",
    response_model=ResponseModel[DialogSyncDetail],
    dependencies=[Security(get_current_active_user, scopes=["tg:dialog_sync:create"])],
)
async def create_dialog_sync(dialog_sync: DialogSyncCreate):
    """
    创建一个新的TG账户。
    - **dialog_sync**: 要创建的TG账户的详细信息。
    """
    dialog_sync_obj = await DialogSync.create(**dialog_sync.dict())
    response = await DialogSyncDetail.from_tortoise_orm(dialog_sync_obj)
    return ResponseModel(data=response)


@dialog_sync_router.get(
    "",
    summary="获取TG对话列表",
    response_model=ResponseModel[PageModel[DialogSyncDetail]],
    dependencies=[Security(get_current_active_user, scopes=["tg:dialog_sync:read"])],
)
async def list_dialog_syncs(
    dialog_sync_filter: ListDialogSyncFilterSet = Depends(),
    pagination: PaginationParams = Depends(),
):
    """
    获取所有TG对话同步的列表。
    """
    query = dialog_sync_filter.apply_filters()
    page_data = await paginate(query, pagination, DialogSyncDetail)
    return ResponseModel(data=page_data)
