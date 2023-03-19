from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from app.orm.core import ORMModel, mixins, str_30

if TYPE_CHECKING:
    from app.orm.product import ProductModel


class TagsModel(mixins.ProductIDMixin, ORMModel):
    name: Mapped[str_30]

    product: Mapped[Optional[ProductModel]] = relationship(ProductModel, back_populates="tags")
