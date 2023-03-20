from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from app.orm.core import ORMModel, str_30

if TYPE_CHECKING:
    from app.orm.category import CategoryModel
    from app.orm.category_property_value import CategoryPropertyValueModel


class CategoryPropertyTypeModel(ORMModel):
    name: Mapped[str_30]

    category: Mapped[List[CategoryModel]] = relationship(
        secondary="categoryproperty",
        back_populates="properties",
    )
    values: Mapped[List[CategoryPropertyValueModel]] = relationship(
        back_populates="type",
    )
