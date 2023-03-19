from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class ProductReviewPhoto(ORMSchema):
    product_review_id: int
    image_url: str
    serial_number: int
