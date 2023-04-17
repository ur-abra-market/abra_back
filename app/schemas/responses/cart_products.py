from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema
from .cart_product import CartProduct


class CartProducts(ApplicationSchema):
    cart_products: Optional[List[CartProduct]] = []
    total_positions: int
    total_cart_count: int
