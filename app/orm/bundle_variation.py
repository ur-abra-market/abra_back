from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .bundle import BundleModel
    from .bundle_variation_pod import BundleVariationPodModel


class BundleVariationModel(ORMModel):
    product_variation_value_id: Mapped[types.variation_value_to_product_fk]
    bundle_id: Mapped[types.bundle_id_fk]
    bundle_variation_pod_id: Mapped[types.bundle_variation_pod_id_fk]

    bundle: Mapped[BundleModel] = relationship(back_populates="values")
    pod: Mapped[BundleVariationPodModel] = relationship(back_populates="bundle_variations")
