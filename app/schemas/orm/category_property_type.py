from __future__ import annotations

from typing import TYPE_CHECKING, List

from app.schemas.orm.schema import ORMSchema

if TYPE_CHECKING:
    from app.schemas.orm.category import Category
    from app.schemas.orm.category_property_value import CategoryPropertyValue


class CategoryPropertyType(ORMSchema):
    name: str
    category: List[Category]
    values: List[CategoryPropertyValue]
