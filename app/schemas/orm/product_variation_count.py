from __future__ import annotations

from typing import Optional

from app.schemas.orm.schema import ORMSchema


class ProductVariationCount(ORMSchema):
    count: int
    product_variation_value1_id: int
    product_variation_value2_id: Optional[int] = None
