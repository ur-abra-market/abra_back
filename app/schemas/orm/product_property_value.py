from __future__ import annotations

from .core import ORMSchema, mixins


class ProductPropertyValue(mixins.ProductIDMixin, ORMSchema):
    property_value_id: int
