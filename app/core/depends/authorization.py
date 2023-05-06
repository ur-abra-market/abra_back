from __future__ import annotations

from typing import Optional

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import crud
from orm import CompanyModel, SellerModel, SupplierModel, UserModel

from .sqlalchemy import get_session


async def account(
    user_id: int,
    session: AsyncSession = Depends(get_session),
) -> Optional[UserModel]:
    user = await crud.users.get.one(
        session=session,
        where=[UserModel.id == user_id],
        options=[
            selectinload(UserModel.notification),
            selectinload(UserModel.admin),
            selectinload(UserModel.seller).selectinload(SellerModel.image),
            selectinload(UserModel.seller).selectinload(SellerModel.addresses),
            selectinload(UserModel.supplier)
            .selectinload(SupplierModel.company)
            .selectinload(CompanyModel.images),
        ],
    )
    if user and user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account was deleted.",
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
