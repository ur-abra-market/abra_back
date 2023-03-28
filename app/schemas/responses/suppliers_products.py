from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from ..schema import ApplicationORMSchema

if TYPE_CHECKING:
    from ..orm import Supplier, Product


class SuppliersProducts(ApplicationORMSchema):
    supplier: Supplier
    products: Optional[List[Product]] = None
