from __future__ import annotations

from pydantic import BaseModel


class OrderIDMixin(BaseModel):
    order_id: int
