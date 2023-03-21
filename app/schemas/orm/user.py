from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import EmailStr

from .schema import ORMSchema

if TYPE_CHECKING:
    from .seller import Seller
    from .supplier import Supplier
    from .user_address import UserAddress
    from .user_image import UserImage
    from .user_notification import UserNotification


class User(ORMSchema):
    email: EmailStr
    phone: str
    created_at: datetime
    updated_at: datetime
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: str
    is_supplier: bool
    images: Optional[List[UserImage]] = None
    addresses: Optional[List[UserAddress]] = None
    notification: Optional[UserNotification] = None
    seller: Optional[Seller] = None
    supplier: Optional[Supplier] = None
