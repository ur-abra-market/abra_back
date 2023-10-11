from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .bundlable_variation_value import BundlableVariationValueModel
    from .bundle_price import BundlePriceModel
    from .bundle_product_variation_value import BundleProductVariationValueModel
    from .product import ProductModel


class BundleModel(mixins.ProductIDMixin, ORMModel):
    prices: Mapped[Optional[List[BundlePriceModel]]] = relationship(back_populates="bundle")
    product: Mapped[Optional[ProductModel]] = relationship(back_populates="bundles")
    variation_values: Mapped[Optional[List[BundlableVariationValueModel]]] = relationship(
        back_populates="bundle"
    )
    variations: Mapped[Optional[List[BundleProductVariationValueModel]]] = relationship(
        back_populates="bundle"
    )
