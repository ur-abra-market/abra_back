from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product
    from .variation_type import VariationType


class VariationValue(ORMSchema):
    value: str
    variation_type_id: int
    type: Optional[VariationType] = None
    products: Optional[List[Product]] = None
