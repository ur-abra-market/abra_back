from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, bool_true, mixins

if TYPE_CHECKING:
    from .supplier import SupplierModel


class SupplierNotificationsModel(mixins.SupplierIDMixin, ORMModel):
    on_advertising_campaigns: Mapped[bool_true]
    on_order_updates: Mapped[bool_true]
    on_order_reminders: Mapped[bool_true]
    on_product_updates: Mapped[bool_true]
    on_product_reminders: Mapped[bool_true]
    on_reviews_of_products: Mapped[bool_true]
    on_change_in_demand: Mapped[bool_true]
    on_advice_from_abra: Mapped[bool_true]
    on_account_support: Mapped[bool_true]

    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="notifications")
