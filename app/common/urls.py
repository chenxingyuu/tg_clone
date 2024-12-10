from fastapi import APIRouter

from app.common.views import common_router

router = APIRouter()
router.include_router(common_router, prefix="/common", tags=["通用"])
