from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .order import OrderModel


class BundleVariationPodAmountModel(mixins.BundleVariationPodIDMixin, ORMModel):
    amount: Mapped[types.int]

    order: Mapped[Optional[OrderModel]] = relationship(back_populates="item")
