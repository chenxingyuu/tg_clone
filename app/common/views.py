from fastapi import APIRouter, HTTPException

from cores.response import ResponseModel

common_router = APIRouter()


@common_router.post(
    "/healthy",
    summary="healthy",
    response_model=ResponseModel,
)
async def healthy():
    return ResponseModel()


import hmac
import hashlib
import subprocess
from fastapi import Request, Header

# GitHub Webhook secret
GITHUB_SECRET = "your_github_secret"


@common_router.post("/github-webhook")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    """
    GitHub Webhook
    功能：接收 GitHub Webhook 通知，自动拉取最新代码
    :param request:
    :param x_hub_signature_256:
    :return:
    """
    # 获取请求体
    body = await request.body()
    # 计算签名
    signature = "sha256=" + hmac.new(GITHUB_SECRET.encode(), body, hashlib.sha256).hexdigest()

    # 比较签名
    if not hmac.compare_digest(signature, x_hub_signature_256):
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 拉取最新代码
    subprocess.run(["git", "pull"], check=True)

    return {"status": "success", "message": "Code pulled successfully"}