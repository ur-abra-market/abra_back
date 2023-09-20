from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .order import Order
    from .order_status import OrderStatus


class OrderStatusHistory(ORMSchema):
    order_id: int
    order_status_id: int
    
    order: Optional[Order] = None
    status: Optional[OrderStatus] = None
