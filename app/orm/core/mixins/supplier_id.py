from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core.types import supplier_id_fk


class SupplierIDMixin:
    supplier_id: Mapped[supplier_id_fk]
