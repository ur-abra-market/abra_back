from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .variation_value import ProductModel, VariationValueModel


class VariationValueToProductModel(mixins.ProductIDMixin, mixins.VariationValueIDMixin, ORMModel):
    product: Mapped[Optional[ProductModel]] = relationship(back_populates="product_variations")
    variation: Mapped[Optional[VariationValueModel]] = relationship(
        back_populates="product_variation"
    )
