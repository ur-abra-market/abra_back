from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .variation_type import VariationTypeModel
    from .variation_value_to_product import VariationValueToProductModel


class VariationValueModel(mixins.VariationTypeIDMixin, ORMModel):
    value: Mapped[types.str_50]

    type: Mapped[Optional[VariationTypeModel]] = relationship(back_populates="values")
    product_variation: Mapped[Optional[VariationValueToProductModel]] = relationship(
        back_populates="variation"
    )
