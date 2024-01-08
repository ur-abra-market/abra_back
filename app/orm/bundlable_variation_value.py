from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .bundle import BundleModel
    from .variation_value_to_product import VariationValueToProductModel


class BundlableVariationValueModel(
    mixins.VariationValueToProductIDMixin,
    mixins.BundleIDMixin,
    ORMModel,
):
    amount: Mapped[types.int]

    bundle: Mapped[Optional[BundleModel]] = relationship(back_populates="variation_values")
    product_variation: Mapped[Optional[VariationValueToProductModel]] = relationship(
        back_populates="bundlable_product_variation_value"
    )
