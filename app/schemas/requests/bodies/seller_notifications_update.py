from __future__ import annotations

from ...schema import ApplicationSchema


class SellerNotificationUpdate(ApplicationSchema):
    on_discount: bool = False
    on_order_updates: bool = False
    on_order_reminders: bool = False
    on_stock_again: bool = False
    on_product_is_cheaper: bool = False
    on_your_favorites_new: bool = False
    on_account_support: bool = False
