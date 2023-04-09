from __future__ import annotations

from .core import ORMSchema, mixins


class Order(mixins.TimestampMixin, mixins.SellerIDMixin, ORMSchema):
    is_car: bool = True
