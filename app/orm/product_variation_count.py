from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from .core import ORMModel, product_variation_value_fk


class ProductVariationCountModel(ORMModel):
    count: Mapped[int]

    product_variation_value1_id: Mapped[product_variation_value_fk]
    product_variation_value2_id: Mapped[Optional[product_variation_value_fk]]
