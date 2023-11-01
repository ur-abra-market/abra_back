from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .company import CompanyModel
    from .product import ProductModel
    from .property_type import PropertyTypeModel
    from .variation_type import VariationTypeModel


class CategoryModel(mixins.ParentCategoryIDMixin, ORMModel):
    name: Mapped[types.str_50]
    level: Mapped[types.small_int]

    parent: Mapped[Optional[CategoryModel]] = relationship(
        "CategoryModel",
        back_populates="children",
        remote_side=lambda: getattr(CategoryModel, "id"),
        lazy="selectin",
        join_depth=2,
    )
    children: Mapped[Optional[List[CategoryModel]]] = relationship(
        "CategoryModel",
        back_populates="parent",
        join_depth=2,
    )
    products: Mapped[Optional[List[ProductModel]]] = relationship(back_populates="category")
    properties: Mapped[Optional[List[PropertyTypeModel]]] = relationship(
        secondary="category_to_property_type",
        back_populates="category",
    )
    variations: Mapped[Optional[List[VariationTypeModel]]] = relationship(
        secondary="category_to_variation_type",
        back_populates="category",
    )
    companies: Mapped[Optional[List[CompanyModel]]] = relationship(
        secondary="company_business_sector_to_category",
        back_populates="business_sectors",
    )

    @hybrid_property
    def hierarchy_ids(self) -> List[int]:
        category_ids = [self.id]
        parent = self.parent
        while parent:
            category_ids.append(parent.id)
            parent = parent.parent

        return category_ids
