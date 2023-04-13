from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product


class Tags(ORMSchema):
    name: str
    product: Optional[Product] = None
