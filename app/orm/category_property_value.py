from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from app.orm.core import ORMModel, category_property_type_fk, str_50

if TYPE_CHECKING:
    from app.orm.category_property_type import CategoryPropertyTypeModel
    from app.orm.product import ProductModel


class CategoryPropertyValueModel(ORMModel):
    value: Mapped[str_50]
    optional_value: Mapped[Optional[str_50]]

    property_type_id: Mapped[category_property_type_fk]

    type: Mapped[Optional[CategoryPropertyTypeModel]] = relationship(
        CategoryPropertyTypeModel, back_populates="values"
    )
    products: Mapped[List[ProductModel]] = relationship(
        ProductModel,
        secondary="product_property_values",
        back_populates="properties",
    )
