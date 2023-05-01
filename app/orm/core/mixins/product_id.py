from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..types import product_id_fk


class ProductIDMixin:
    product_id: Mapped[product_id_fk]
