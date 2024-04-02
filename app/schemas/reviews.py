from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from .schema import ApplicationSchema

if TYPE_CHECKING:
    from .product_for_reviews import ProductForReviews
    from .product_review import ProductReview


class Reviews(ApplicationSchema):
    product: ProductForReviews
    product_review: Optional[List[ProductReview]]
    feedbacks: Optional[Dict]
