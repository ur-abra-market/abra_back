from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .bundlable_variation_value import BundlableVariationValueModel
    from .bundle_price import BundlePriceModel
    from .bundle_product_variation_value import BundleProductVariationValueModel
    from .product import ProductModel
    from .variation_value_to_product import VariationValueToProductModel


class BundleModel(mixins.ProductIDMixin, ORMModel):
    name: Mapped[Optional[types.str_100]]
    prices: Mapped[Optional[List[BundlePriceModel]]] = relationship(back_populates="bundle")
    product: Mapped[Optional[ProductModel]] = relationship(back_populates="bundles")
    variation_values: Mapped[Optional[List[BundlableVariationValueModel]]] = relationship(
        back_populates="bundle", lazy="selectin"
    )
    variations: Mapped[Optional[List[BundleProductVariationValueModel]]] = relationship(
        back_populates="bundle"
    )

    @hybrid_property
    def pickable_variations(self) -> Optional[List[VariationValueToProductModel]]:
        if not self.variation_values:
            return None
        bundlable_type = self.variation_values[0].product_variation.variation.type.id
        return [
            variation
            for variation in self.product.product_variations
            if not variation.variation.type.id == bundlable_type
        ]
