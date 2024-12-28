from tortoise.contrib.pydantic import pydantic_model_creator

from app.tg.models import Account

AccountDetail = pydantic_model_creator(
    Account,
    name="AccountDetail",
    include=(
        "id", "name", "phone", "api_id", "api_hash", "channel_count"
    ),
)

AccountCreate = pydantic_model_creator(
    Account,
    name="AccountCreate",
    include=(
        "name", "phone", "password", "api_id", "api_hash"
    ),
)

AccountUpdate = AccountCreate
AccountPatch = AccountCreate
