from __future__ import annotations

from typing import Optional

from ...schema import ApplicationSchema


class SellerNotificationUpdate(ApplicationSchema):
    on_discount: Optional[bool] = None
    on_order_updates: Optional[bool] = None
    on_order_reminders: Optional[bool] = None
    on_stock_again: Optional[bool] = None
    on_product_is_cheaper: Optional[bool] = None
    on_your_favorites_new: Optional[bool] = None
    on_account_support: Optional[bool] = None
