from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .schema import ORMSchema

if TYPE_CHECKING:
    from .product import Product


class Tags(ORMSchema):
    product_id: int
    name: str
    product: Optional[Product] = None
