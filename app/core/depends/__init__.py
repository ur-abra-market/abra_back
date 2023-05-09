from typing import Optional

from fastapi.param_functions import Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from orm import UserModel

from .authorization import authorization, authorization_optional, authorization_refresh
from .files import FileObjects, image_required
from .role import admin, seller, supplier
from .sqlalchemy import get_session

AuthJWT = Annotated[AuthJWT, Depends()]
Authorization = Annotated[UserModel, Depends(authorization)]
AuthorizationRefresh = Annotated[UserModel, Depends(authorization_refresh)]
AuthorizationOptional = Annotated[Optional[UserModel], Depends(authorization_optional)]
AdminAuthorization = Annotated[UserModel, Depends(admin)]
SellerAuthorization = Annotated[UserModel, Depends(seller)]
SupplierAuthorization = Annotated[UserModel, Depends(supplier)]
DatabaseSession = Annotated[AsyncSession, Depends(get_session)]
Image = Annotated[FileObjects, Depends(image_required)]

__all__ = (
    "authorization",
    "AuthJWT",
    "Authorization",
    "AuthorizationRefresh",
    "AuthorizationOptional",
    "AdminAuthorization",
    "SellerAuthorization",
    "SupplierAuthorization",
    "admin",
    "seller",
    "supplier",
    "DatabaseSession",
    "Image",
    "FileObjects",
)
