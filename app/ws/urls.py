from fastapi import APIRouter

from app.ws.message import message_router

router = APIRouter()
router.include_router(message_router, prefix="", tags=["消息转发"])
