from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .bundle import BundleModel


class BundlePriceModel(mixins.BundleIDMixin, ORMModel):
    price: Mapped[Optional[types.decimal_10_3]]
    discount: Mapped[Optional[types.decimal_3_2]]
    start_date: Mapped[types.datetime]
    end_date: Mapped[types.datetime]
    min_quantity: Mapped[types.int]

    bundle: Mapped[BundleModel] = relationship(back_populates="prices")
