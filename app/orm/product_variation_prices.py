from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .variation_value_to_product import VariationValueToProductModel


class ProductVariationPriceModel(mixins.VariationValueToProductIDMixin, ORMModel):
    price: Mapped[types.decimal_10_2]
    discount: Mapped[types.decimal_3_2]

    product_variation_value: Mapped[Optional[VariationValueToProductModel]] = relationship(
        back_populates="prices"
    )
