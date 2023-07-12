from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .supplier import Supplier


class SupplierNotifications(ORMSchema):
    on_advertising_campaigns: bool = True
    on_order_updates: bool = True
    on_order_reminders: bool = True
    on_product_updates: bool = True
    on_product_reminders: bool = True
    on_reviews_of_products: bool = True
    on_change_in_demand: bool = True
    on_advice_from_abra: bool = True
    on_account_support: bool = True
    supplier: Optional[Supplier] = None
