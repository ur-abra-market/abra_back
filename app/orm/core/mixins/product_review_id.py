from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core.types import product_review_id_fk


class ProductReviewIDMixin:
    product_review_id: Mapped[product_review_id_fk]
