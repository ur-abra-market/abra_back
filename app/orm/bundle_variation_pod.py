from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel

if TYPE_CHECKING:
    from .bundle_variation import BundleVariationModel


class BundleVariationPodModel(ORMModel):
    bundle_variations: Mapped[List[BundleVariationModel]] = relationship(back_populates="pod")
