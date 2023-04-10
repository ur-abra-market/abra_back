from __future__ import annotations

from pydantic import BaseModel


class CategoryIDMixin(BaseModel):
    category_id: int
