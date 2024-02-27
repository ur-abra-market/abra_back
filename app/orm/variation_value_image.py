from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .variation_value_to_product import VariationValueToProductModel


class VariationValueImageModel(mixins.VariationValueToProductIDMixin, ORMModel):
    image_url: Mapped[types.text]
    thumbnail_url: Mapped[types.text]
    order: Mapped[Optional[types.small_int]]
    variation: Mapped[Optional[VariationValueToProductModel]] = relationship(
        back_populates="images"
    )
