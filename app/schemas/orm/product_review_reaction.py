from __future__ import annotations

from .core import ORMSchema


class ProductReviewReaction(ORMSchema):
    reaction: bool
