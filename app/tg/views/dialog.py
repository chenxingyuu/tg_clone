from fastapi import Security, APIRouter, Depends

from app.system.views.auth import get_current_active_user
from app.tg.filters import ListDialogFilterSet
from app.tg.serializers.dialog import DialogDetail
from cores.paginate import PageModel, PaginationParams, paginate
from cores.response import ResponseModel

dialog_router = APIRouter()


@dialog_router.get(
    "",
    summary="获取TG对话列表",
    response_model=ResponseModel[PageModel[DialogDetail]],
    dependencies=[Security(get_current_active_user, scopes=["tg:dialog:read"])],
)
async def list_dialogs(
    dialog_filter: ListDialogFilterSet = Depends(),
    pagination: PaginationParams = Depends(),
):
    """
    获取所有TG对话的列表。
    """
    query = dialog_filter.apply_filters()
    page_data = await paginate(query, pagination, DialogDetail)
    return ResponseModel(data=page_data)
