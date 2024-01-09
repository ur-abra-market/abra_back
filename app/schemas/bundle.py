from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .bundlable_variation_value import BundlableVariationValue
    from .bundle_price import BundlePrice
    from .product import Product
    from .variation_value_to_product import VariationValueToProduct


class Bundle(ORMSchema):
    prices: Optional[List[BundlePrice]] = None
    product: Optional[Product] = None
    variation_values: Optional[List[BundlableVariationValue]] = None

    pickable_variations: Optional[List[VariationValueToProduct]] = None
