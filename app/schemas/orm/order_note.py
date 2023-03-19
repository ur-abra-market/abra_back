from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class OrderNote(ORMSchema):
    text: str
    order_product_variation_id: int
