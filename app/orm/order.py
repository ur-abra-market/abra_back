from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .bundle_variation_pod_amount import BundleVariationPodAmountModel
    from .order_status_history import OrderStatusHistoryModel
    from .seller import SellerModel


class OrderModel(
    mixins.SellerIDMixin,
    ORMModel,
):
    is_cart: Mapped[types.bool_true]

    status_history: Mapped[Optional[List[OrderStatusHistoryModel]]] = relationship(back_populates="order")
    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="orders")
    details: Mapped[Optional[List[BundleVariationPodAmountModel]]] = relationship(back_populates="order")
