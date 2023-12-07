from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product

from typing_ import DictStrAny


class ProductImage(ORMSchema):
    image_url: str
    order: int
    product: Optional[Product] = None
    thumbnail_urls: Optional[DictStrAny] = None
