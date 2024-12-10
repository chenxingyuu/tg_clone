from typing import Generic, TypeVar

from pydantic import BaseModel
from tortoise.queryset import QuerySet

T = TypeVar("T")


class FilterSet(BaseModel, Generic[T]):
    def apply_filters(self, query: QuerySet[T]) -> QuerySet[T]:
        for key, value in self.dict(exclude_none=True).items():
            query = query.filter(**{f"{key}__icontains": value})
        return query
