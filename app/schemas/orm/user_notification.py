from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class UserNotification(ORMSchema):
    user_id: int
    on_discount: bool = True
    on_order_updates: bool = True
    on_order_reminders: bool = True
    on_stock_again: bool = True
    on_product_is_cheaper: bool = True
    on_your_favorites_new: bool = True
    on_account_support: bool = True
