from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .bundle import Bundle
    from .variation_value_to_product import VariationValueToProduct


class BundlableVariationValue(ORMSchema):
    variation_value_to_product_id: int
    bundle_id: int
    amount: int

    bundle: Optional[Bundle] = None
    product_variation: Optional[VariationValueToProduct] = None
