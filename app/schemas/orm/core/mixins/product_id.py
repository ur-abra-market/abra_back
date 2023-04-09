from __future__ import annotations

from pydantic import BaseModel


class ProductIDMixin(BaseModel):
    product_id: int
