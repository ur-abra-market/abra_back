from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import product_review_id_fk
from ..types import product_review_id_fk_type


class ProductReviewIDMixin:
    product_review_id: Mapped[product_review_id_fk_type] = product_review_id_fk
