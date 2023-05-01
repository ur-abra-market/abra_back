from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .seller import Seller
    from .supplier import Supplier
    from .user_notification import UserNotification


class User(
    mixins.EmailMixin, mixins.NameMixin, mixins.PhoneMixin, mixins.TimestampMixin, ORMSchema
):
    is_supplier: bool
    is_verified: bool = False
    is_deleted: bool = False
    notification: Optional[UserNotification] = None
    seller: Optional[Seller] = None
    supplier: Optional[Supplier] = None
