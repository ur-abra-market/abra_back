from __future__ import annotations

from .core import ORMSchema


class CategoryProperty(ORMSchema):
    category_id: int
    property_type_id: int
