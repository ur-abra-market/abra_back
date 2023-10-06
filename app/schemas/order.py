from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .bundle_variation_pod_amount import BundleVariationPodAmount
    from .order_status import OrderStatus
    from .seller import Seller


class Order(ORMSchema):
    is_cart: bool

    seller: Optional[Seller] = None
    status: Optional[OrderStatus] = None
    details: Optional[List[BundleVariationPodAmount]] = None
