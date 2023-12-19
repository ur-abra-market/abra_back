from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .bundle import BundleModel
    from .bundle_variation_pod import BundleVariationPodModel
    from .variation_value_to_product import VariationValueToProductModel


class BundleProductVariationValueModel(
    mixins.BundleIDMixin,
    mixins.VariationValueToProductIDMixin,
    mixins.BundleVariationPodIDMixin,
    ORMModel,
):
    bundle: Mapped[Optional[BundleModel]] = relationship(back_populates="variations")
    pod: Mapped[Optional[BundleVariationPodModel]] = relationship(
        back_populates="bundle_variations"
    )
    product_variation: Mapped[Optional[VariationValueToProductModel]] = relationship(
        backref="bundle_product_variation_values"
    )
