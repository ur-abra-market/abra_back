from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .order import OrderModel
    from .order_status import OrderStatusModel


class OrderStatusHistoryModel(
    mixins.OrderIDMixin,
    mixins.OrderStatusIDMixin,
    ORMModel,
):
    order: Mapped[Optional[OrderModel]] = relationship(back_populates="status_history")
    status: Mapped[Optional[OrderStatusModel]] = relationship(back_populates="orders")
