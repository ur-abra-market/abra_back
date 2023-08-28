from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .bundle_variation_pod_amount import BundleVariationPodAmount
    from .order_status import OrderStatus
    from .seller import Seller


class Order(mixins.TimestampMixin, ORMSchema):
    is_cart: bool
    bundle_variation_pod_amount_id: int

    seller: Optional[Seller] = None
    status: Optional[OrderStatus] = None
    item: Optional[BundleVariationPodAmount] = None
