from __future__ import annotations

from ...schema import ApplicationSchema


class SupplierNotificationUpdate(ApplicationSchema):
    on_advertising_campaigns: bool = False
    on_order_updates: bool = False
    on_order_reminders: bool = False
    on_product_updates: bool = False
    on_product_reminders: bool = False
    on_reviews_of_products: bool = False
    on_change_in_demand: bool = False
    on_advice_from_abra: bool = False
    on_account_support: bool = False
