from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product


class ProductImage(ORMSchema):
    image_url: str
    order: int
    product: Optional[Product] = None
