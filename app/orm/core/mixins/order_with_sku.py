from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..types import order_with_sku_id_fk


class OrderWithSkuIDMixin:
    order_with_sku_id: Mapped[order_with_sku_id_fk]
