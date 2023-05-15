from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from enums.user_type import UserType

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .seller import Seller
    from .supplier import Supplier
    from .user_notification import UserNotification


class User(
    mixins.EmailMixin, mixins.NameMixin, mixins.PhoneMixin, mixins.TimestampMixin, ORMSchema
):
    type: UserType
    is_verified: bool = False
    is_deleted: bool = False
    is_supplier: bool = False
    notification: Optional[UserNotification] = None
    seller: Optional[Seller] = None
    supplier: Optional[Supplier] = None
