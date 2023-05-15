from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..types import sku_id_fk


class SkuIDMixin:
    sku_id: Mapped[sku_id_fk]
