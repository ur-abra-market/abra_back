from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product
    from .variation_value import VariationValue


class VariationValueToProduct(ORMSchema):
    variation_value_id: int
    product_id: int

    variation: Optional[VariationValue] = None
    product: Optional[Product] = None
