from typing import Optional

from pydantic import Field
from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from app.system.models import Menu, Permission, Role, User
from cores.filter import FilterSet


class ListPermissionFilterSet(FilterSet):
    name: Optional[str] = Field(None, description="name")
    description: Optional[str] = Field(None, description="description")

    def apply_filters(self, query: QuerySet[Permission] = None) -> QuerySet[Permission]:
        if not query:
            query = Permission.get_queryset().all()
        if self.name:
            query = query.filter(Q(name__icontains=self.name))
        if self.description:
            query = query.filter(Q(description__icontains=self.description))
        return query


class ListRoleFilterSet(ListPermissionFilterSet):
    def apply_filters(self, query: QuerySet[Role] = None) -> QuerySet[Role]:
        if not query:
            query = Role.get_queryset().all()
        if self.name:
            query = query.filter(Q(name__icontains=self.name))
        if self.description:
            query = query.filter(Q(description__icontains=self.description))
        return query

    #


class ListUserFilterSet(FilterSet):
    username: Optional[str] = Field(None, description="按用户名过滤")
    email: Optional[str] = Field(None, description="按电子邮件过滤")
    is_active: Optional[bool] = Field(None, description="按是否激活状态过滤")
    is_superuser: Optional[bool] = Field(None, description="按超级用户状态过滤")

    def apply_filters(self, query: QuerySet[User] = None) -> QuerySet[User]:
        if not query:
            query = User.get_queryset().all()
        if self.username:
            query = query.filter(Q(username__icontains=self.username))
        if self.email:
            query = query.filter(Q(email__icontains=self.email))
        if self.is_active is not None:
            query = query.filter(Q(is_active=self.is_active))
        if self.is_superuser is not None:
            query = query.filter(Q(is_superuser=self.is_superuser))
        return query


class ListMenuFilterSet(FilterSet):
    name: Optional[str] = Field(None, description="按用户名过滤")
    path: Optional[str] = Field(None, description="按电子邮件过滤")

    def apply_filters(self, query: QuerySet[Menu] = None) -> QuerySet[Menu]:
        if not query:
            query = Menu.get_queryset().all()
        if self.name:
            query = query.filter(Q(name__icontains=self.name))
        if self.path:
            query = query.filter(Q(path__icontains=self.path))
        return query
