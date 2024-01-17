from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .category import Category
    from .property_value import ProductPropertyValue, PropertyValue


class PropertyTypeBase(ORMSchema):
    name: str
    has_optional_value: bool
    category: Optional[List[Category]] = None


class PropertyType(PropertyTypeBase):
    values: Optional[List[PropertyValue]] = None


class ProductPropertyType(PropertyTypeBase):
    values: Optional[List[ProductPropertyValue]] = None
