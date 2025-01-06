from tortoise.contrib.pydantic import pydantic_model_creator

from app.tg.models import DialogSync

DialogSyncDetail = pydantic_model_creator(
    DialogSync,
    name="DialogSyncDetail",
    include=("id", "account_id", "from_dialog_id", "to_dialog_id", "type", "status", "settings", "created_at", "updated_at"),
)

DialogSyncCreate = pydantic_model_creator(
    DialogSync,
    name="DialogSyncCreate",
    include=(
        "account_id", "from_dialog_id", "to_dialog_id", "type", "status", "settings"
    ),
)
