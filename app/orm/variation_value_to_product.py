from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from product import ProductModel, ProductVariationPriceModel

    from .bundlable_variation_value import BundlableVariationValueModel
    from .variation_value import VariationValueModel


class VariationValueToProductModel(mixins.ProductIDMixin, mixins.VariationValueIDMixin, ORMModel):
    product: Mapped[Optional[ProductModel]] = relationship(
        back_populates="product_variations",
    )
    variation: Mapped[Optional[VariationValueModel]] = relationship(
        back_populates="product_variation", lazy="selectin"
    )
    prices: Mapped[Optional[List[ProductVariationPriceModel]]] = relationship(
        back_populates="product_variation_value",
        lazy="selectin",
    )
    bundlable_product_variation_value: Mapped[
        Optional[BundlableVariationValueModel]
    ] = relationship(back_populates="product_variation")
