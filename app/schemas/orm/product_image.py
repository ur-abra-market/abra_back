from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .product import Product


class ProductImage(mixins.ProductIDMixin, ORMSchema):
    image_url: str
    serial_number: int
    product: Optional[Product] = None
