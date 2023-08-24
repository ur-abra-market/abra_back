from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, types


class VariationValueImageModel(ORMModel):
    variation_value_id: Mapped[types.variation_value_to_product_fk]

    image_url: Mapped[types.text]
    thumbnail_url: Mapped[types.text]
