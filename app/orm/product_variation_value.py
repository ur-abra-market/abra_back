from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, category_variation_value_fk, mixins


class ProductVariationValueModel(mixins.ProductIDMixin, ORMModel):
    variation_value_id: Mapped[category_variation_value_fk]
