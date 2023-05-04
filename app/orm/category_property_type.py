from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, str_30

if TYPE_CHECKING:
    from .category import CategoryModel
    from .category_property_value import CategoryPropertyValueModel


class CategoryPropertyTypeModel(ORMModel):
    name: Mapped[str_30]

    colors: Mapped[List] = ["White",
                            "Beige",
                            "Sand",
                            "Gray",
                            "Black",
                            "Metallic",
                            "Bronze",
                            "Red",
                            "Orange",
                            "Yellow",
                            "Green",
                            "Blue",
                            "Indigo",
                            "Lilac",
                            "Purple",]

    category: Mapped[List[CategoryModel]] = relationship(
        secondary="category_property",
        back_populates="properties",
    )
    values: Mapped[List[CategoryPropertyValueModel]] = relationship(back_populates="type")
