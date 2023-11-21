from __future__ import annotations

from typing import Optional

from corecrud import Options, Where
from fastapi.param_functions import Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core import exceptions
from core.app import crud
from orm import CompanyModel, SellerAddressModel, SellerModel, SupplierModel, UserModel

from .sqlalchemy import get_session


async def account(
    user_id: int,
    session: AsyncSession = Depends(get_session),
) -> Optional[UserModel]:
    user = await crud.users.select.one(
        Where(UserModel.id == user_id),
        Options(
            selectinload(UserModel.seller).selectinload(SellerModel.image),
            selectinload(UserModel.seller)
            .selectinload(SellerModel.addresses)
            .selectinload(SellerAddressModel.country),
            selectinload(UserModel.seller).selectinload(SellerModel.notifications),
            selectinload(UserModel.supplier)
            .selectinload(SupplierModel.company)
            .selectinload(CompanyModel.images),
            selectinload(UserModel.supplier)
            .selectinload(SupplierModel.company)
            .selectinload(CompanyModel.phone),
            selectinload(UserModel.supplier).selectinload(SupplierModel.notifications),
        ),
        session=session,
    )
    if user and user.is_deleted:
        raise exceptions.ForbiddenException(
            detail="This account was deleted",
        )

    return user


async def authorization_refresh(
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
) -> UserModel:
    authorize.jwt_refresh_token_required()

    return await account(user_id=authorize.get_jwt_subject(), session=session)


async def authorization(
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
) -> UserModel:
    authorize.jwt_required()

    return await account(user_id=authorize.get_jwt_subject(), session=session)


async def authorization_optional(
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Optional[UserModel]:
    authorize.jwt_optional()

    return await account(user_id=authorize.get_jwt_subject(), session=session)
