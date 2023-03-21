from __future__ import annotations

from .schema import ORMSchema


class CategoryProperty(ORMSchema):
    category_id: int
    property_type_id: int
