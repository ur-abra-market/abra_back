from __future__ import annotations

from .core import ORMSchema, mixins


class ProductImage(mixins.ProductIDMixin, ORMSchema):
    image_url: str
    serial_number: int
