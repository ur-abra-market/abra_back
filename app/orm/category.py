from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, category_id_fk, str_50

if TYPE_CHECKING:
    from .category_property_type import CategoryPropertyTypeModel
    from .category_variation_type import CategoryVariationTypeModel
    from .product import ProductModel
    from .sku import SkuModel


class CategoryModel(ORMModel):
    name: Mapped[str_50]
    level: Mapped[int]

    parent_id: Mapped[Optional[category_id_fk]]

    children: Mapped[List[CategoryModel]] = relationship()
    products: Mapped[List[ProductModel]] = relationship(back_populates="category")
    properties: Mapped[List[CategoryPropertyTypeModel]] = relationship(
        secondary="category_property",
        back_populates="category",
    )
    variations: Mapped[List[CategoryVariationTypeModel]] = relationship(
        secondary="category_variation",
        back_populates="category",
    )
    skus: Mapped[Optional[List[SkuModel]]] = relationship(
        back_populates="category", secondary="category_sku"
    )
