from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product
    from .product_review_photo import ProductReviewPhoto


class ProductReview(ORMSchema):
    text: str
    grade_overall: int
    datetime: dt.datetime
    product: Optional[Product] = None
    photos: Optional[List[ProductReviewPhoto]] = None
