from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, bool_true, mixins


class UserNotificationModel(mixins.UserIDMixin, ORMModel):
    on_discount: Mapped[bool_true]
    on_order_updates: Mapped[bool_true]
    on_order_reminders: Mapped[bool_true]
    on_stock_again: Mapped[bool_true]
    on_product_is_cheaper: Mapped[bool_true]
    on_your_favorites_new: Mapped[bool_true]
    on_account_support: Mapped[bool_true]
