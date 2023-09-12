from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .bundle import BundleModel


class BundlableVariationValueModel(
    mixins.ProductIDMixin,
    mixins.VariationTypeIDMixin,
    mixins.VariationValueIDMixin,
    mixins.BundleIDMixin,
    ORMModel,
):
    amount: Mapped[types.int]

    bundle: Mapped[BundleModel] = relationship(back_populates="variation_values")
