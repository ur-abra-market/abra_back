from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from .core import ORMModel, types


class ProductVariationCountModel(ORMModel):
    count: Mapped[types.big_int]

    product_variation_value1_id: Mapped[types.product_variation_value_fk]
    product_variation_value2_id: Mapped[Optional[types.product_variation_value_fk]]
