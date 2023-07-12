from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .supplier import SupplierModel


class SupplierNotificationsModel(mixins.SupplierIDMixin, ORMModel):
    on_advertising_campaigns: Mapped[types.bool_true]
    on_order_updates: Mapped[types.bool_true]
    on_order_reminders: Mapped[types.bool_true]
    on_product_updates: Mapped[types.bool_true]
    on_product_reminders: Mapped[types.bool_true]
    on_reviews_of_products: Mapped[types.bool_true]
    on_change_in_demand: Mapped[types.bool_true]
    on_advice_from_abra: Mapped[types.bool_true]
    on_account_support: Mapped[types.bool_true]

    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="notifications")
