from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..types import sku_product_id_fk


class SkuProductIDMixin:
    sku_product_id: Mapped[sku_product_id_fk]
