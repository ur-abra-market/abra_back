from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class ProductPropertyValue(ORMSchema):
    product_id: int
    property_value_id: int
