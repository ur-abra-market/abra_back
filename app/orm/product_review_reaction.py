from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, mixins


class ProductReviewReactionModel(mixins.ProductReviewIDMixin, mixins.SellerIDMixin, ORMModel):
    reaction: Mapped[bool]
