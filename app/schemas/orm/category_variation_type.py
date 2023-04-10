from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .category import Category
    from .category_variation_value import CategoryVariationValue


class CategoryVariationType(ORMSchema):
    name: str
    category: Optional[List[Category]] = None
    values: Optional[List[CategoryVariationValue]] = None
