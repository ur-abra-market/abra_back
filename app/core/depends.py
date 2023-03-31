import imghdr
from dataclasses import dataclass
from typing import Optional

from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends, File
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.tools import store
from orm import UserModel
from orm.core import async_sessionmaker
from schemas import JWT, User

__all__ = (
    "get_session",
    "UserObjects",
    "auth_refresh_token_required",
    "auth_required",
    "auth_optional",
)


async def get_session() -> AsyncSession:
    async with async_sessionmaker.begin() as session:
        yield session


def get_jwt_subject(authorize: AuthJWT) -> JWT:
    subject = authorize.get_jwt_subject()
    return JWT() if subject is None else JWT.parse_raw(subject)


@dataclass
class UserObjects:
    schema: Optional[User] = None
    orm: Optional[UserModel] = None


async def auth_core(authorize: AuthJWT, session: AsyncSession) -> Optional[User]:
    jwt = get_jwt_subject(authorize=authorize)

    return await store.orm.users.get_one(
        session=session,
        options=[joinedload(UserModel.seller), joinedload(UserModel.supplier)],
        where=[UserModel.id == jwt.user_id],
    )


async def auth_refresh_token_required(
    authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
) -> JWT:
    authorize.jwt_refresh_token_required()

    user = await auth_core(authorize=authorize, session=session)
    return UserObjects(schema=User.from_orm(user), orm=user)


async def auth_required(
    authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
) -> UserObjects:
    authorize.jwt_required()

    user = await auth_core(authorize=authorize, session=session)
    return UserObjects(schema=User.from_orm(user), orm=user)


async def auth_optional(
    authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
) -> UserObjects:
    authorize.jwt_optional()

    user = await auth_core(authorize=authorize, session=session)
    return UserObjects(schema=None if user is None else User.from_orm(user), orm=user)
