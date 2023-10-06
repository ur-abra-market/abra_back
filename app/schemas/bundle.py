from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .bundlable_variation_value import BundlableVariationValue
    from .product import Product


class Bundle(ORMSchema):
    product: Optional[Product] = None
    variation_values: Optional[List[BundlableVariationValue]] = None
