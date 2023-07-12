from __future__ import annotations

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from starlette import status

from orm import UserModel

from .authorization import authorization


async def seller(user: UserModel = Depends(authorization)) -> UserModel:
    if not user.seller:
        raise HTTPException(
            detail="Seller not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return user


async def supplier(user: UserModel = Depends(authorization)) -> UserModel:
    if not user.supplier:
        raise HTTPException(
            detail="Supplier not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return user
