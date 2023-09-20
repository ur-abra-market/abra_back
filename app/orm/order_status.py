from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .order_status_history import OrderStatusHistoryModel


class OrderStatusModel(ORMModel):
    name: Mapped[types.str_20]
    title: Mapped[types.str_20]

    orders: Mapped[List[OrderStatusHistoryModel]] = relationship(back_populates="status")
