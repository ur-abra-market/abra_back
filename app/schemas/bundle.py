from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .bundlable_variation_value import BundlableVariationValue
    from .product import Product


class Bundle(ORMSchema):
    amount: int

    product: Optional[Product] = None
    values: Optional[List[BundlableVariationValue]] = None
