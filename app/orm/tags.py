from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .product import ProductModel


class TagModel(ORMModel):
    name: Mapped[types.str_30]

    product: Mapped[Optional[ProductModel]] = relationship(
        back_populates="tags", secondary="product_tag"
    )
