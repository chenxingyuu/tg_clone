from fastapi import APIRouter

from app.tg.views.account import account_router

router = APIRouter()
router.include_router(account_router, prefix="/accounts", tags=["TG/账户"])
