from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class ProductImage(ORMSchema):
    product_id: int
    image_url: str
    serial_number: int
