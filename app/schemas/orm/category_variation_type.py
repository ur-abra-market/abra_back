from __future__ import annotations

from typing import TYPE_CHECKING, List

from app.schemas.orm.schema import ORMSchema

if TYPE_CHECKING:
    from app.schemas.orm.category import Category
    from app.schemas.orm.category_variation_value import CategoryVariationValue


class CategoryVariationType(ORMSchema):
    name: str
    category: List[Category]
    values: List[CategoryVariationValue]
