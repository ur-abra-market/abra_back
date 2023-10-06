from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import order_status_fk
from ..types import order_status_fk_type


class OrderStatusIDMixin:
    order_status_id: Mapped[order_status_fk_type] = order_status_fk
