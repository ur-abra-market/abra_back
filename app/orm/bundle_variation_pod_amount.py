from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .order import OrderModel


class BundleVariationPodAmountModel(ORMModel):
    bundle_variation_pod_id: Mapped[types.bundle_variation_pod_id_fk]
    amount: Mapped[types.int]

    order: Mapped[Optional[OrderModel]] = relationship(back_populates="item")
