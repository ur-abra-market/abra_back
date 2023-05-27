from __future__ import annotations

from typing import Optional

from ...schema import ApplicationSchema


class SupplierNotificationUpdate(ApplicationSchema):
    on_advertising_campaigns: Optional[bool] = None
    on_order_updates: Optional[bool] = None
    on_order_reminders: Optional[bool] = None
    on_product_updates: Optional[bool] = None
    on_product_reminders: Optional[bool] = None
    on_reviews_of_products: Optional[bool] = None
    on_change_in_demand: Optional[bool] = None
    on_advice_from_abra: Optional[bool] = None
    on_account_support: Optional[bool] = None
