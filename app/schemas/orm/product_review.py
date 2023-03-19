from __future__ import annotations

from datetime import datetime

from app.schemas.orm.schema import ORMSchema


class ProductReview(ORMSchema):
    product_id: int
    seller_id: int
    text: str
    grade_overall: int
    datetime: datetime
