from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .order_status import OrderStatus
    from .seller import Seller


class Order(mixins.TimestampMixin, ORMSchema):
    is_cart: bool
    seller: Optional[Seller] = None
    status: Optional[OrderStatus] = None
