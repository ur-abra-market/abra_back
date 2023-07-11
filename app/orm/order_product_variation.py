from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, types


class OrderProductVariationModel(mixins.OrderIDMixin, mixins.StatusIDMixin, ORMModel):
    count: Mapped[types.small_int]

    product_variation_count_id: Mapped[types.product_variation_count_fk]
