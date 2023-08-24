from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .bundle import BundleModel


class BundlableVariationValueModel(mixins.ProductIDMixin, ORMModel):
    variation_type_id: Mapped[types.variation_type_fk]
    variation_value_id: Mapped[types.variation_value_fk]
    bundle_id: Mapped[types.bundle_id_fk]

    bundle: Mapped[BundleModel] = relationship(back_populates="values")
