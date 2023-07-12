from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .seller import SellerModel


class SellerNotificationsModel(mixins.SellerIDMixin, ORMModel):
    on_discount: Mapped[types.bool_true]
    on_order_updates: Mapped[types.bool_true]
    on_order_reminders: Mapped[types.bool_true]
    on_stock_again: Mapped[types.bool_true]
    on_product_is_cheaper: Mapped[types.bool_true]
    on_your_favorites_new: Mapped[types.bool_true]
    on_account_support: Mapped[types.bool_true]

    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="notifications")
