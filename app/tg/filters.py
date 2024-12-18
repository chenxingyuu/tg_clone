from typing import Optional

from pydantic import Field
from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from app.tg.models import Account
from cores.filter import FilterSet


class ListAccountFilterSet(FilterSet):
    name: Optional[str] = Field(None, description="name")
    status: Optional[int] = Field(None, description="status")

    def apply_filters(self, query: QuerySet[Account] = None) -> QuerySet[Account]:
        if not query:
            query = Account.get_queryset().all()
        if self.name is not None:
            query = query.filter(Q(name__icontains=self.name))
        if self.status is not None:
            query = query.filter(Q(status=self.status))
        return query
