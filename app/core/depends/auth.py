from __future__ import annotations

from typing import Optional, cast

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.app import crud
from orm import CompanyModel, SellerModel, SupplierModel, UserModel
from schemas import JWT

from .sqlalchemy import get_session


def get_jwt_subject(authorize: AuthJWT) -> JWT:
    subject = authorize.get_jwt_subject()
    return JWT() if subject is None else cast(JWT, JWT.parse_raw(subject))


async def auth_core(authorize: AuthJWT, session: AsyncSession) -> Optional[UserModel]:
    jwt = get_jwt_subject(authorize=authorize)

    user = await crud.users.get.one(
        session=session,
        where=[UserModel.id == jwt.user_id],
        options=[
            joinedload(UserModel.notification),
            joinedload(UserModel.admin),
            joinedload(UserModel.seller).joinedload(SellerModel.image),
            joinedload(UserModel.seller).joinedload(SellerModel.addresses),
            joinedload(UserModel.supplier)
            .joinedload(SupplierModel.company)
            .joinedload(CompanyModel.images),
        ],
    )
    if user and user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account was deleted.",
        )

    return user


async def auth_refresh_token_required(
    authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
) -> UserModel:
    authorize.jwt_refresh_token_required()

    return await auth_core(authorize=authorize, session=session)


async def auth_required(
    authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
) -> UserModel:
    authorize.jwt_required()

    return await auth_core(authorize=authorize, session=session)


async def auth_optional(
    authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
) -> Optional[UserModel]:
    authorize.jwt_optional()

    return await auth_core(authorize=authorize, session=session)
