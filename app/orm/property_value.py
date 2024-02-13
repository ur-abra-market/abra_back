from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .product import ProductModel
    from .property_type import PropertyTypeModel
    from .property_value_to_product import PropertyValueToProductModel


class PropertyValueModel(mixins.PropertyTypeIDMixin, ORMModel):
    value: Mapped[types.str_50]

    type: Mapped[Optional[PropertyTypeModel]] = relationship(back_populates="values")
    products: Mapped[List[ProductModel]] = relationship(
        secondary="property_value_to_product",
        back_populates="properties",
        viewonly=True,
    )
    property_value_product: Mapped[List[PropertyValueToProductModel]] = relationship(
        back_populates="property_value",
        viewonly=True,
    )
    optional_value: AssociationProxy[List[str]] = association_proxy(
        "property_value_product",
        "optional_value",
    )
    property_value_product: Mapped[List[PropertyValueToProductModel]] = relationship(
        back_populates="property_value"
    )
    optional_value: AssociationProxy[List[str]] = association_proxy(
        "property_value_product", "optional_value"
    )
