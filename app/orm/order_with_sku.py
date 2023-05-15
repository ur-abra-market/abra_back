from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, bool_true, mixins

if TYPE_CHECKING:
    # from .order_status import OrderStatusModel
    # from .seller import SellerModel
    from .sku_product import SkuProductModel


class OrderWithSkuModel(
    mixins.TimestampMixin, mixins.SellerIDMixin, mixins.StatusIDMixin, ORMModel
):
    """заказ с использованием SKU"""

    is_cart: Mapped[bool_true]
    # TODO: добавить в эти таблицы relationship OrderWithSkuModel
    # status: Mapped[Optional[OrderStatusModel]] = relationship(back_populates="orders")
    # seller: Mapped[Optional[SellerModel]] = relationship(back_populates="orders")
    count: Mapped[int]
    sku_products: Mapped[List[SkuProductModel]] = relationship(
        back_populates="orders", secondary="order_sku_product"
    )
