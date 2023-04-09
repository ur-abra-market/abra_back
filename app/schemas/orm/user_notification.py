from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .user import User


class UserNotification(mixins.UserIDMixin, ORMSchema):
    on_discount: bool = True
    on_order_updates: bool = True
    on_order_reminders: bool = True
    on_stock_again: bool = True
    on_product_is_cheaper: bool = True
    on_your_favorites_new: bool = True
    on_account_support: bool = True
    user: Optional[User] = None
