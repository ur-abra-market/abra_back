from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import product_id_fk
from ..types import product_id_fk_type


class ProductIDMixin:
    product_id: Mapped[product_id_fk_type] = product_id_fk
