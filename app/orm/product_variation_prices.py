from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .variation_value_to_product import VariationValueToProductModel


class ProductVariationPriceModel(mixins.VariationValueToProductIDMixin, ORMModel):
    value: Mapped[types.decimal_10_3]
    multiplier: Mapped[types.decimal_10_5]
    discount: Mapped[types.decimal_3_2]
    start_date: Mapped[types.datetime]
    end_date: Mapped[types.datetime]
    min_quantity: Mapped[types.int]

    product_variation_value: Mapped[Optional[VariationValueToProductModel]] = relationship(
        back_populates="prices"
    )
