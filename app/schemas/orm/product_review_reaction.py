from __future__ import annotations

from .core import ORMSchema, mixins


class ProductReviewReaction(mixins.ProductReviewIDMixin, mixins.SellerIDMixin, ORMSchema):
    reaction: bool
