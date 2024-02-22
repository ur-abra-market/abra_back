from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .product import ProductModel
    from .property_value import PropertyValueModel


class PropertyValueToProductModel(mixins.ProductIDMixin, mixins.PropertyValueIDMixin, ORMModel):
    optional_value: Mapped[Optional[types.str_50]]
    property_value: Mapped[PropertyValueModel] = relationship(
        back_populates="property_value_product",
        viewonly=True,
    )
    product: Mapped[ProductModel] = relationship(
        back_populates="property_value_product",
        viewonly=True,
    )
