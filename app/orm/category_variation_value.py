from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from app.orm.core import ORMModel, category_variation_type_fk, str_50

if TYPE_CHECKING:
    from app.orm.category_variation_type import CategoryVariationTypeModel
    from app.orm.product import ProductModel


class CategoryVariationValueModel(ORMModel):
    variation_type_id: Mapped[category_variation_type_fk]
    value: Mapped[str_50]

    type: Mapped[Optional[CategoryVariationTypeModel]] = relationship(
        CategoryVariationTypeModel, back_populates="values"
    )
    products: Mapped[List[ProductModel]] = relationship(
        ProductModel,
        secondary="product_variation_values",
        back_populates="variations",
    )
