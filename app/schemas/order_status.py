from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .order import Order


class OrderStatus(ORMSchema):
    name: str
    orders: Optional[List[Order]] = None
