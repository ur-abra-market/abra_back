from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product
    from .product_review_photo import ProductReviewPhoto
    from .product_review_reaction import ProductReviewReaction


class ProductReview(ORMSchema):
    text: str
    grade_overall: int

    product: Optional[Product] = None
    photos: Optional[List[ProductReviewPhoto]] = None
    reactions: Optional[List[ProductReviewReaction]] = None
