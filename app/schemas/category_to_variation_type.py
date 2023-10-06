from __future__ import annotations

from .core import ORMSchema


class CategoryToVariationType(ORMSchema):
    category_id: int
    variation_type_id: int
