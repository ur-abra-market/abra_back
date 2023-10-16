from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .product import ProductModel
    from .property_type import PropertyTypeModel


class PropertyValueModel(mixins.PropertyTypeIDMixin, ORMModel):
    value: Mapped[types.str_50]
    has_optional_value: Mapped[types.bool_false]
    optional_value: Mapped[Optional[types.str_50]]

    type: Mapped[Optional[PropertyTypeModel]] = relationship(back_populates="values")
    products: Mapped[List[ProductModel]] = relationship(
        secondary="property_value_to_product",
        back_populates="properties",
    )
