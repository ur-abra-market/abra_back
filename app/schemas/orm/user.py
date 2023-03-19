from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from app.schemas.orm.schema import ORMSchema
from pydantic import EmailStr

if TYPE_CHECKING:
    from app.schemas.orm.seller import Seller
    from app.schemas.orm.supplier import Supplier
    from app.schemas.orm.user_address import UserAddress
    from app.schemas.orm.user_credentials import UserCredentials
    from app.schemas.orm.user_image import UserImage
    from app.schemas.orm.user_notification import UserNotification


class User(ORMSchema):
    email: EmailStr
    phone: str
    created_at: datetime
    updated_at: datetime
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: str
    is_supplier: bool
    credentials: Optional[UserCredentials] = None
    images: List[UserImage]
    addresses: List[UserAddress]
    notification: Optional[UserNotification] = None
    seller: Optional[Seller] = None
    supplier: Optional[Supplier] = None
