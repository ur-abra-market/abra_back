from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from app.orm.core import ORMModel, str_30

if TYPE_CHECKING:
    from app.orm.category import CategoryModel
    from app.orm.category_variation_value import CategoryVariationValueModel


class CategoryVariationTypeModel(ORMModel):
    name: Mapped[str_30]

    category: Mapped[List[CategoryModel]] = relationship(
        secondary="categoryvariation",
        back_populates="variations",
    )
    values: Mapped[List[CategoryVariationValueModel]] = relationship(
        back_populates="type"
    )
