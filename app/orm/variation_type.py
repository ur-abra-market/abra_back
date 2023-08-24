from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .category import CategoryModel
    from .variation_value import VariationValueModel


class VariationTypeModel(ORMModel):
    name: Mapped[types.str_30]

    category: Mapped[List[CategoryModel]] = relationship(
        secondary="category_to_variation_type",
        back_populates="variations",
    )
    values: Mapped[List[VariationValueModel]] = relationship(back_populates="type")
