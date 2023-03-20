from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from app.orm.core import ORMModel, str_50

if TYPE_CHECKING:
    from app.orm.category_property_type import CategoryPropertyTypeModel
    from app.orm.category_variation_type import CategoryVariationTypeModel
    from app.orm.product import ProductModel


class CategoryModel(ORMModel):
    name: Mapped[str_50]
    level: Mapped[int]

    parent_id: Mapped[Optional[int]]

    products: Mapped[List[ProductModel]] = relationship(back_populates="category")
    properties: Mapped[List[CategoryPropertyTypeModel]] = relationship(
        secondary="categoryproperty",
        back_populates="category",
    )
    variations: Mapped[List[CategoryVariationTypeModel]] = relationship(
        secondary="categoryvariation",
        back_populates="category",
    )
