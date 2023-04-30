from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, str_20

if TYPE_CHECKING:
    from .order import OrderModel


class OrderStatusModel(ORMModel):
    name: Mapped[str_20]

    orders: Mapped[List[OrderModel]] = relationship(back_populates="status")
