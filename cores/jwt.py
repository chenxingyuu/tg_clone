from datetime import datetime, timedelta
from typing import Optional, List

from jose import jwt
from pydantic import BaseModel

from cores.config import settings


class Token(BaseModel):
    access_token: str
    token_type: str
    scopes: List[str]


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = timedelta(days=settings.security.token_expire_days),
):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(
        to_encode,
        settings.security.secret_key,
        algorithm=settings.security.algorithm,
    )


def verify_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.security.secret_key,
        algorithms=[settings.security.algorithm],
    )
