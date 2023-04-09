from __future__ import annotations

from pydantic import BaseModel


class SupplierIDMixin(BaseModel):
    supplier_id: int
