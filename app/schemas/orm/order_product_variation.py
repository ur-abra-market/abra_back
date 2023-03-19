from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class OrderProductVariation(ORMSchema):
    order_id: int
    status_id: int
    count: int
    product_variation_count_id: int
