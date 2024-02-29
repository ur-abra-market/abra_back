from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .bundle_variation_pod_amount import BundleVariationPodAmount
    from .order_status_history import OrderStatusHistory
    from .seller import Seller


class OrderHistory(ORMSchema):
    seller: Optional[Seller] = None
    details: Optional[List[BundleVariationPodAmount]] = None
    status_history: Optional[List[OrderStatusHistory]] = None
    total_order_price: int = 0
