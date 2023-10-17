from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .category import CategoryModel
    from .property_value import PropertyValueModel


class PropertyTypeModel(ORMModel):
    name: Mapped[types.str_30]
    has_optional_value: Mapped[types.bool_false]

    category: Mapped[List[CategoryModel]] = relationship(
        secondary="category_to_property_type",
        back_populates="properties",
    )
    values: Mapped[List[PropertyValueModel]] = relationship(back_populates="type")
