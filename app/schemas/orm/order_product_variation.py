from __future__ import annotations

from .core import ORMSchema, mixins


class OrderProductVariation(mixins.OrderIDMixin, mixins.StatusIDMixin, ORMSchema):
    count: int
    product_variation_count_id: int
