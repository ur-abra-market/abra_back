from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, text


class ProductReviewModel(mixins.ProductIDMixin, mixins.SellerIDMixin, ORMModel):
    text: Mapped[text]
    grade_overall: Mapped[int]
    datetime: Mapped[datetime]
