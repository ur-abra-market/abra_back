from __future__ import annotations

from .core import ORMSchema, mixins


class Order(mixins.TimestampMixin, ORMSchema):
    is_cart: bool
