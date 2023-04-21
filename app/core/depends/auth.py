from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, cast

from fastapi.param_functions import Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.app import crud
from orm import SupplierModel, UserModel
from schemas import JWT, User

from .sqlalchemy import get_session


def get_jwt_subject(authorize: AuthJWT) -> JWT:
    subject = authorize.get_jwt_subject()
    return JWT() if subject is None else cast(JWT, JWT.parse_raw(subject))


@dataclass(
    repr=False,
    eq=False,
    frozen=True,
)
class UserObjects:
    schema: Optional[User] = None
    orm: Optional[UserModel] = None


async def auth_core(authorize: AuthJWT, session: AsyncSession) -> Optional[UserModel]:
    jwt = get_jwt_subject(authorize=authorize)

    return await crud.users.get_one_by(
        session=session,
        id=jwt.user_id,
        options=[
            joinedload(UserModel.seller),
            joinedload(UserModel.supplier).joinedload(SupplierModel.company),
        ],
    )


async def auth_refresh_token_required(
    authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
) -> UserObjects:
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
