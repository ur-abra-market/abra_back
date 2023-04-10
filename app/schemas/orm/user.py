from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .seller import Seller
    from .supplier import Supplier
    from .user_address import UserAddress
    from .user_image import UserImage
    from .user_notification import UserNotification


class User(mixins.EmailMixin, mixins.PhoneMixin, mixins.TimestampMixin, ORMSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    is_supplier: bool
    is_verified: bool = False
    image: Optional[UserImage] = None
    addresses: Optional[List[UserAddress]] = None
    notification: Optional[UserNotification] = None
    seller: Optional[Seller] = None
    supplier: Optional[Supplier] = None
