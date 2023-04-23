from __future__ import annotations

from .core import ORMSchema


class CategoryVariation(ORMSchema):
    category_id: int
    variation_type_id: int
