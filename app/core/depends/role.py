from __future__ import annotations

from fastapi.param_functions import Depends

from core import exceptions
from orm import UserModel

from .authorization import authorization


async def seller(user: UserModel = Depends(authorization)) -> UserModel:
    if not user.seller:
        raise exceptions.NotFoundException(
            detail="Seller not found",
        )

    return user


async def supplier(user: UserModel = Depends(authorization)) -> UserModel:
    if not user.supplier:
        raise exceptions.NotFoundException(
            detail="Supplier not found",
        )

    return user
