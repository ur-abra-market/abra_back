from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .product import ProductModel


class BrandModel(ORMModel):
    name: Mapped[types.str_50] = mapped_column(unique=True)

    products: Mapped[List[ProductModel]] = relationship(back_populates="brand")
