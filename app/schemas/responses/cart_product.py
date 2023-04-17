from __future__ import annotations

from ..schema import ApplicationSchema


class CartProduct(ApplicationSchema):
    order_id: int
    seller_id: int
    product_name: str
    product_description: str
    cart_count: int
    stock_count: int
    price_value: float
    discount: float
