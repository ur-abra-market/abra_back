from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .bundle_variation_pod import BundleVariationPodModel
    from .order import OrderModel


class BundleVariationPodAmountModel(
    mixins.BundleVariationPodIDMixin, mixins.OrderIDMixin, ORMModel
):
    amount: Mapped[types.int]

    order: Mapped[Optional[OrderModel]] = relationship(back_populates="details")
    bundle_variation_pod: Mapped[Optional[BundleVariationPodModel]] = relationship(back_populates="bundle_variation_pod_amount")
