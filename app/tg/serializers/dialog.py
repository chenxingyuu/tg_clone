from tortoise.contrib.pydantic import pydantic_model_creator

from app.tg.models import Dialog

DialogDetail = pydantic_model_creator(
    Dialog,
    name="DialogDetail",
    exclude=("account",),
)
