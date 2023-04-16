from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, bool_true, mixins

if TYPE_CHECKING:
    from .user import UserModel


class UserNotificationModel(mixins.UserIDMixin, ORMModel):
    on_discount: Mapped[bool_true]
    on_order_updates: Mapped[bool_true]
    on_order_reminders: Mapped[bool_true]
    on_stock_again: Mapped[bool_true]
    on_product_is_cheaper: Mapped[bool_true]
    on_your_favorites_new: Mapped[bool_true]
    on_account_support: Mapped[bool_true]

    user: Mapped[Optional[UserModel]] = relationship(back_populates="notification")
