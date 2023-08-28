from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .company import CompanyModel
    from .product import ProductModel
    from .property_type import PropertyTypeModel
    from .variation_type import VariationTypeModel


class CategoryModel(ORMModel):
    name: Mapped[types.str_50]
    level: Mapped[types.small_int]

    parent_id: Mapped[Optional[types.category_id_fk]]

    children: Mapped[List[CategoryModel]] = relationship()
    products: Mapped[List[ProductModel]] = relationship(back_populates="category")
    properties: Mapped[List[PropertyTypeModel]] = relationship(
        secondary="category_to_property_type",
        back_populates="category",
    )
    variations: Mapped[List[VariationTypeModel]] = relationship(
        secondary="category_variation",
        back_populates="category",
    )
    companies: Mapped[List[CompanyModel]] = relationship(
        secondary="company_business_sector_to_category",
        back_populates="business_sectors",
    )
