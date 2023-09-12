from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .product import ProductModel
    from .variation_type import VariationTypeModel


class VariationValueModel(mixins.VariationTypeIDMixin, ORMModel):
    value: Mapped[types.str_50]

    type: Mapped[Optional[VariationTypeModel]] = relationship(back_populates="values")
    products: Mapped[List[ProductModel]] = relationship(
        secondary="variation_value_to_product",
        back_populates="variations",
    )
