from typing import Optional

from pydantic import Field
from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from app.tg.models import Account, Dialog
from cores.filter import FilterSet


class ListAccountFilterSet(FilterSet):
    name: Optional[str] = Field(None, description="name")
    phone: Optional[str] = Field(None, description="phone")

    def apply_filters(self, query: QuerySet[Account] = None) -> QuerySet[Account]:
        if not query:
            query = Account.get_queryset().all()
        if self.name is not None:
            query = query.filter(Q(name__icontains=self.name))
        if self.phone is not None:
            query = query.filter(Q(phone__icontains=self.phone))
        return query


class ListDialogFilterSet(FilterSet):
    title: Optional[str] = Field(None, description="title")
    username: Optional[str] = Field(None, description="username")
    account_id: Optional[int] = Field(None, description="account_id")
    tg_id: Optional[int] = Field(None, description="tg_id")
    status: Optional[int] = Field(None, description="status")

    def apply_filters(self, query: QuerySet[Dialog] = None) -> QuerySet[Dialog]:
        if not query:
            query = Dialog.get_queryset().all()
        if self.title is not None:
            query = query.filter(Q(title__icontains=self.title))
        if self.username is not None:
            query = query.filter(Q(username__icontains=self.username))
        if self.account_id is not None:
            query = query.filter(Q(account__id=self.account_id))
        if self.tg_id is not None:
            query = query.filter(Q(tg_id=self.tg_id))
        if self.status is not None:
            query = query.filter(Q(status=self.status))
        return query
