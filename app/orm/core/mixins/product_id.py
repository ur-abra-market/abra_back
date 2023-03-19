from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core.types import product_id_fk


class ProductIDMixin:
    product_id: Mapped[product_id_fk]
