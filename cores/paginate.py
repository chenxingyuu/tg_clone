from dataclasses import dataclass
from typing import Generic, List, Type, TypeVar

from fastapi import Query
from ghkit.enum import GEnum
from pydantic import BaseModel
from tortoise.contrib.pydantic import PydanticModel
from tortoise.queryset import QuerySet

T = TypeVar("T")


class OrderType(GEnum):
    DESC = "desc", "-"
    ASC = "asc", ""


class PageModel(BaseModel, Generic[T]):
    list: List[T]
    total: int
    page: int
    limit: int


@dataclass
class PaginationParams:
    page: int = Query(1, alias="page", ge=1)
    limit: int = Query(10, alias="limit", ge=1)
    sort_by: List[str] = Query(None, alias="sort_by")
    sort_order: List[OrderType] = Query(None, alias="sort_order")

    def apply_sorting(self, queryset: QuerySet[T]) -> QuerySet[T]:
        if not self.sort_by:
            return queryset

        if self.sort_order is None:
            self.sort_order = [OrderType.DESC]

        if len(self.sort_order) < len(self.sort_by):
            self.sort_order = [
                *self.sort_order,
                *self.sort_order[-1:] * (len(self.sort_by) - len(self.sort_order)),
            ]

        queryset = queryset.order_by(
            *[f"{order.desc}{field}" for field, order in zip(self.sort_by, self.sort_order)]
        )

        return queryset


async def paginate(
    queryset: QuerySet[T],
    pagination: PaginationParams,
    schema: Type[PydanticModel],
) -> PageModel[T]:
    total = await queryset.count()
    queryset = (
        pagination.apply_sorting(queryset)
        .offset((pagination.page - 1) * pagination.limit)
        .limit(pagination.limit)
    )
    items = await schema.from_queryset(queryset)
    return PageModel(
        list=items,
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )
