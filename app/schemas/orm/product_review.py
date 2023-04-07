from __future__ import annotations

import datetime as dt

from .schema import ORMSchema


class ProductReview(ORMSchema):
    product_id: int
    seller_id: int
    text: str
    grade_overall: int
    datetime: dt.datetime
