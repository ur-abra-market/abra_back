from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product_review import ProductReview


class ProductReviewPhoto(ORMSchema):
    image_url: str
    serial_number: int
    review: Optional[ProductReview] = None
