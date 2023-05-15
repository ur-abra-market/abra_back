from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, str_200

if TYPE_CHECKING:
    from .sku import SkuModel


class BrandModel(mixins.SupplierIDMixin, ORMModel):
    name: Mapped[str_200]
    skus: Mapped[Optional[List[SkuModel]]] = relationship(back_populates="brand")
    # TODO: понять у бренда один саплаер или много
    # suppliers: Mapped[List[SupplierModel]] = relationship(back_populates="brands")
