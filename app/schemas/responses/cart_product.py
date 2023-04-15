from __future__ import annotations

from ..schema import ApplicationSchema


class CartProduct(ApplicationSchema):
    seller_id: int
    cart_count: int
    stock_count: int
