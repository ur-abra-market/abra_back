from __future__ import annotations

from .schema import ORMSchema


class OrderNote(ORMSchema):
    text: str
    order_product_variation_id: int
