from fastapi import APIRouter

from app.tg.views.account import account_router
from app.tg.views.dialog import dialog_router

router = APIRouter()
router.include_router(account_router, prefix="/accounts", tags=["TG/账户"])
router.include_router(dialog_router, prefix="/dialogs", tags=["TG/对话"])
