from __future__ import annotations

from pydantic import BaseModel


class SellerIDMixin(BaseModel):
    seller_id: int
