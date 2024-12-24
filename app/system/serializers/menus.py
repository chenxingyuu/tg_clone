from typing import List, Optional

from pydantic import BaseModel, Field
from tortoise.contrib.pydantic import pydantic_model_creator

from app.system.models import Menu


class MenuMeta(BaseModel):
    locale: Optional[str] = Field(default=None)
    icon: Optional[str] = Field(default=None)
    requires_auth: bool = Field(default=False)
    order: int = Field(default=0)
    hide_in_menu: bool = Field(default=False)
    hide_children_in_menu: bool = Field(default=False)
    no_affix: bool = Field(default=False)
    ignore_cache: bool = Field(default=False)


class MenuDetail2(BaseModel):
    id: int
    name: str
    path: str
    components: str
    meta: MenuMeta
    parent_id: Optional[int] = Field(default=0)

    class Config:
        from_attributes = True


MenuDetail = pydantic_model_creator(
    Menu,
    name="MenuDetail",
    include=(
        "id",
        "name",
        "path",
        "components",
        "meta_locale",
        "meta_icon",
        "meta_requires_auth",
        "meta_order",
        "meta_hide_in_menu",
        "meta_hide_children_in_menu",
        "meta_no_affix",
        "meta_ignore_cache",
        "parent_id",
    ),
)


class MenuDetailTree(MenuDetail2):
    children: Optional[List["MenuDetailTree"]] = Field(default_factory=list)

    @classmethod
    def from_menu_list(cls, menus: List[Menu]) -> List["MenuDetailTree"]:
        menus = [
            MenuDetail2(
                id=menu.id,
                name=menu.name,
                path=menu.path,
                components=menu.components,
                parent_id=menu.parent_id,  # noqa
                meta=MenuMeta(
                    locale=menu.meta_locale,
                    icon=menu.meta_icon,
                    requires_auth=menu.meta_requires_auth,
                    order=menu.meta_order,
                    hide_in_menu=menu.meta_hide_in_menu,
                    hide_children_in_menu=menu.meta_hide_children_in_menu,
                    no_affix=menu.meta_no_affix,
                    ignore_cache=menu.meta_ignore_cache,
                ),
            ) for menu in menus]

        menu_dict = {menu.id: cls.model_validate(menu) for menu in menus}
        tree = []

        for menu in menus:
            menu_tree = menu_dict[menu.id]
            if menu_tree.parent_id is None:
                tree.append(menu_tree)
            else:
                parent = menu_dict.get(menu_tree.parent_id)
                if parent:
                    parent.children.append(menu_tree)
        return tree


MenuCreate = pydantic_model_creator(
    Menu,
    name="MenuCreate",
    include=(
        "name",
        "path",
        "components",
        "meta_locale",
        "meta_icon",
        "meta_requires_auth",
        "meta_order",
        "meta_hide_in_menu",
        "meta_hide_children_in_menu",
        "meta_no_affix",
        "meta_ignore_cache",
        "parent_id",
    ),
)

MenuUpdate = MenuCreate
MenuPatch = MenuCreate
