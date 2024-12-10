from typing import Generic, Optional, TypeVar

from ghkit.enum import GEnum
from pydantic import BaseModel

T = TypeVar("T")


class ResponseCode(GEnum):
    SUCCESS = 20000, "Success"


class ResponseModel(BaseModel, Generic[T]):
    code: ResponseCode = ResponseCode.SUCCESS
    msg: str = code.desc
    data: Optional[T] = None
