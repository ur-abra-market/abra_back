from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, bool_true, mixins

if TYPE_CHECKING:
    from .order_status import OrderStatusModel
    from .seller import SellerModel


class OrderModel(mixins.TimestampMixin, mixins.SellerIDMixin, mixins.StatusIDMixin, ORMModel):
    is_cart: Mapped[bool_true]

    status: Mapped[Optional[OrderStatusModel]] = relationship(back_populates="orders")
    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="orders")
