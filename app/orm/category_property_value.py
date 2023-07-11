from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .category_property_type import CategoryPropertyTypeModel
    from .product import ProductModel


class CategoryPropertyValueModel(ORMModel):
    value: Mapped[types.str_50]
    optional_value: Mapped[Optional[types.str_50]]

    property_type_id: Mapped[types.category_property_type_fk]

    type: Mapped[Optional[CategoryPropertyTypeModel]] = relationship(back_populates="values")
    products: Mapped[List[ProductModel]] = relationship(
        secondary="product_property_value",
        back_populates="properties",
    )
