from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, types


class VariationValueToProductModel(mixins.ProductIDMixin, ORMModel):
    variation_value_id: Mapped[types.variation_value_fk]
