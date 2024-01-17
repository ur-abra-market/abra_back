from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from pydantic import validator

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product
    from .property_type import PropertyType


class PropertyValueBase(ORMSchema):
    value: str


class PropertyValue(PropertyValueBase):
    property_type_id: int
    type: Optional[PropertyType] = None
    products: Optional[List[Product]] = None


class ProductPropertyValue(PropertyValueBase):
    optional_value: Optional[str] = None

    @validator("optional_value", pre=True)
    def convert_optional_value_to_str(cls, value):
        return value[0]
