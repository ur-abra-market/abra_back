from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, sku_id_fk

if TYPE_CHECKING:
    from .order_with_sku import OrderWithSkuModel


class SkuProductModel(mixins.ProductIDMixin, ORMModel):
    """
    Артикул+Продукт -> вся инфа о товаре вместе с постоянными и варьирующимеся характеристикам,
    а также количеством на складе.
    """

    sku_id: Mapped[sku_id_fk]
    count: Mapped[int]
    orders: Mapped[Optional[List[OrderWithSkuModel]]] = relationship(
        back_populates="sku_products", secondary="order_sku_product"
    )
