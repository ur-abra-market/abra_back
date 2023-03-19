from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, mixins


class ProductReviewModel(mixins.ProductIDMixin, mixins.SellerIDMixin, ORMModel):
    text: Mapped[str]
    grade_overall: Mapped[int]
    datetime: Mapped[datetime]
