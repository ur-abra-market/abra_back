from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .category_variation_type import CategoryVariationTypeModel
    from .product import ProductModel


class CategoryVariationValueModel(ORMModel):
    value: Mapped[types.str_50]

    variation_type_id: Mapped[types.category_variation_type_fk]

    type: Mapped[Optional[CategoryVariationTypeModel]] = relationship(back_populates="values")
    products: Mapped[List[ProductModel]] = relationship(
        secondary="product_variation_value",
        back_populates="variations",
    )
