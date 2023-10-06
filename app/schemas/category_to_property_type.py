from __future__ import annotations

from .core import ORMSchema


class CategoryToPropertyType(ORMSchema):
    category_id: int
    property_type_id: int
