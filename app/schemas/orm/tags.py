from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .product import Product


class Tags(mixins.ProductIDMixin, ORMSchema):
    name: str
    product: Optional[Product] = None
