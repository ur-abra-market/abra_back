from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .bundle import BundleModel
    from .bundle_variation_pod import BundleVariationPodModel


class BundleVariationModel(
    mixins.BundleIDMixin,
    mixins.VariationValueToProductIDMixin,
    mixins.BundleVariationPodIDMixin,
    ORMModel,
):
    bundle: Mapped[BundleModel] = relationship(back_populates="variations")
    pod: Mapped[BundleVariationPodModel] = relationship(back_populates="bundle_variations")
