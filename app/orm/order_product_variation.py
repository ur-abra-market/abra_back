from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, product_variation_count_fk


class OrderProductVariationModel(mixins.OrderIDMixin, mixins.StatusIDMixin, ORMModel):
    count: Mapped[int]

    product_variation_count_id: Mapped[product_variation_count_fk]
