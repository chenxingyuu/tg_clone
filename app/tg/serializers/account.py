from tortoise.contrib.pydantic import pydantic_model_creator

from app.tg.models import Account

AccountDetail = pydantic_model_creator(
    Account,
    name="AccountDetail",
)


class AccountDetailPagination(AccountDetail):
    dialog_count: int


AccountCreate = pydantic_model_creator(
    Account,
    name="AccountCreate",
    include=(
        "name", "phone", "password", "api_id", "api_hash"
    ),
)

AccountPatch = AccountCreate
