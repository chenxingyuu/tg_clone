from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from passlib.exc import InvalidTokenError
from pydantic import BaseModel, ValidationError
from starlette import status
from tortoise.expressions import Q

from app.system.models import User
from app.system.serializers.users import UserDetail
from cores.jwt import Token, create_access_token, verify_token
from cores.pwd import verify_password
from cores.response import ResponseModel
from cores.scope import filter_scopes, scopes

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/oauth2/password", scopes=scopes)


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []


async def authenticate_user(username: str, password: str) -> Union[bool, User]:
    user = (
        await User.get_queryset()
        .prefetch_related("roles__permissions")
        .get_or_none(Q(username=username) | Q(email=username))
    )
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def authenticate_user_by_oauth(username: str) -> Union[bool, User]:
    user = (
        await User.get_queryset()
        .prefetch_related("roles__permissions")
        .get_or_none(Q(username=username) | Q(email=username))
    )
    if not user:
        return False
    return user


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = verify_token(token)

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    user = (
        await User.get_queryset()
        .prefetch_related("roles__permissions")
        .get_or_none(username=username)
    )
    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        for user_scope in token_data.scopes:
            if scope == user_scope or scope.startswith(f"{user_scope}:"):
                break
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_active_user(
    current_user: User = Security(get_current_user),
) -> UserDetail:
    if current_user.is_active:
        return current_user
    raise HTTPException(status_code=400, detail="Inactive user")


@auth_router.post("/password", response_model=ResponseModel[Token])
async def login_from_password(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # 查询权限
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.name)

    filter_permissions = filter_scopes(permissions)

    access_token = create_access_token(data={"sub": user.username, "scopes": filter_permissions})
    return ResponseModel(
        data=Token(
            access_token=access_token,
            token_type="bearer",
            scopes=filter_permissions,
        )
    )


@auth_router.post("/oauth2/password", response_model=Token)
async def login_from_oauth2_password(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # 查询权限
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.name)

    permissions &= set(form_data.scopes)
    if len(permissions) < len(form_data.scopes):
        raise HTTPException(
            status_code=400, detail=f"Incorrect permission {set(form_data.scopes) - permissions}"
        )

    filter_permissions = filter_scopes(permissions)

    access_token = create_access_token(data={"sub": user.username, "scopes": filter_permissions})
    return Token(
        access_token=access_token,
        token_type="bearer",
        scopes=filter_permissions,
    )


@auth_router.post("/logout", response_model=ResponseModel)
async def logout():
    return ResponseModel()
