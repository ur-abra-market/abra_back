from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product
    from .product_variation_prices import ProductVariationPrice
    from .variation_value import VariationValue


class VariationValueToProduct(ORMSchema):
    variation_value_id: int
    product_id: int

    variation: Optional[VariationValue] = None
    product: Optional[Product] = None
    prices: Optional[List[ProductVariationPrice]] = None
