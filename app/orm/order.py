from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, bool_true, mixins


class OrderModel(mixins.SellerIDMixin, ORMModel):
    datetime: Mapped[datetime]
    is_car: Mapped[bool_true]
