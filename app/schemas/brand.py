from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product


class Brand(ORMSchema):
    name: str

    products: Optional[List[Product]] = None
