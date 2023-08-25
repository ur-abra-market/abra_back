from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .bundle_variation_pod_amount import BundleVariationPodAmountModel
    from .order_status import OrderStatusModel
    from .seller import SellerModel


class OrderModel(mixins.TimestampMixin, mixins.SellerIDMixin, mixins.StatusIDMixin, ORMModel):
    is_cart: Mapped[types.bool_true]
    bundle_variation_pod_amount_id: Mapped[types.bundle_variation_pod_amount_id_fk]

    status: Mapped[Optional[OrderStatusModel]] = relationship(back_populates="orders")
    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="orders")
    item: Mapped[Optional[BundleVariationPodAmountModel]] = relationship(back_populates="order")
