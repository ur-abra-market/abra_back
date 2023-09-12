from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import supplier_id_fk
from ..types import supplier_id_fk_type


class SupplierIDMixin:
    supplier_id: Mapped[supplier_id_fk_type] = supplier_id_fk
