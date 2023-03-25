from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, bool_true, mixins


class OrderModel(mixins.TimestampMixin, mixins.SellerIDMixin, ORMModel):
    is_car: Mapped[bool_true]
