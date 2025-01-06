import traceback

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from cores.config import settings
from cores.log import LOG
from cores.messager import MESSAGE_FACTORY


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            LOG.exception(e)
            # 捕获异常，准备发送飞书告警
            if settings.feishu.alert:
                error_trace = traceback.format_exc()
                await self.send_feishu_alert(request, e, error_trace)
            # 返回统一的错误响应
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )

    @classmethod
    async def send_feishu_alert(cls, request: Request, exception: Exception, traceback_str: str):
        message_dict = {
            "config": {},
            "i18n_elements": {
                "zh_cn": [
                    {"tag": "markdown", "content": f"**URL: 【{request.method}】{request.url}** ", "text_align": "left",
                     "text_size": "normal"},
                    {"tag": "markdown", "content": f"**异常:** {str(exception)}", "text_align": "left", "text_size": "normal"},
                    {"tag": "markdown", "content": traceback_str, "text_align": "left", "text_size": "normal"},
                ]
            },
            "i18n_header": {
                "zh_cn": {
                    "title": {"tag": "plain_text", "content": "🚨服务端错误告警🚨"},
                    "subtitle": {"tag": "plain_text", "content": ""},
                    "template": "blue",
                }
            },
        }
        await MESSAGE_FACTORY.async_send_alarm(message_dict)
