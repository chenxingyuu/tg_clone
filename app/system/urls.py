# app/system/urls.py

from fastapi import APIRouter

from app.system.views.auth import auth_router
from app.system.views.menus import menu_router
from app.system.views.permissions import permission_router
from app.system.views.roles import role_router
from app.system.views.roles_menus import role_menu_router
from app.system.views.roles_permissions import role_permission_router
from app.system.views.users import user_router
from app.system.views.users_me import user_me_router
from app.system.views.users_permissions import user_permission_route
from app.system.views.users_roles import user_role_route

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["系统/授权"])
router.include_router(user_me_router, prefix="/users", tags=["系统/用户/我"])
router.include_router(user_role_route, prefix="/users", tags=["系统/用户/角色"])
router.include_router(user_permission_route, prefix="/users", tags=["系统/用户/权限"])
router.include_router(user_router, prefix="/users", tags=["系统/用户"])
router.include_router(role_router, prefix="/roles", tags=["系统/角色"])
router.include_router(role_permission_router, prefix="/roles", tags=["系统/角色/权限"])
router.include_router(permission_router, prefix="/permissions", tags=["系统/权限"])
router.include_router(menu_router, prefix="/menus", tags=["系统/菜单"])
router.include_router(role_menu_router, prefix="/roles", tags=["系统/角色/菜单"])
