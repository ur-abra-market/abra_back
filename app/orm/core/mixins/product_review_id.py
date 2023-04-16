from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..types import product_review_id_fk


class ProductReviewIDMixin:
    product_review_id: Mapped[product_review_id_fk]
