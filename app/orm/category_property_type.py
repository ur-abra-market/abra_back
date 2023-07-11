from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .category import CategoryModel
    from .category_property_value import CategoryPropertyValueModel


class CategoryPropertyTypeModel(ORMModel):
    name: Mapped[types.str_30]

    category: Mapped[List[CategoryModel]] = relationship(
        secondary="category_property",
        back_populates="properties",
    )
    values: Mapped[List[CategoryPropertyValueModel]] = relationship(back_populates="type")
