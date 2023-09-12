from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .bundlable_variation_value import BundlableVariationValueModel
    from .bundle_variation import BundleVariationModel
    from .product import ProductModel


class BundleModel(mixins.ProductIDMixin, ORMModel):
    stock: Mapped[types.int]

    product: Mapped[ProductModel] = relationship(back_populates="bundles")
    variation_values: Mapped[List[BundlableVariationValueModel]] = relationship(
        back_populates="bundle"
    )
    variations: Mapped[List[BundleVariationModel]] = relationship(back_populates="bundle")
