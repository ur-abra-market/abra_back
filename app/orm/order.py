from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, bool_true, mixins


class OrderModel(mixins.TimestampMixin, mixins.SellerIDMixin, mixins.StatusIDMixin, ORMModel):
    is_cart: Mapped[bool_true]
