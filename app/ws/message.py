from fastapi import APIRouter, HTTPException

from cores.constant.socket import WsMessage
from cores.sio import sio

message_router = APIRouter()


@message_router.post("/message_proxy")
async def send_message(message: WsMessage):
    try:
        await sio.emit(event=message.event, data=message.data, room=message.room)
        return {"status": "success", "message": "消息已发送"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
