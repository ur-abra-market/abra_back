from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .bundle_variation_pod import BundleVariationPodModel


class BundleVariationPodPriceModel(mixins.BundleVariationPodIDMixin, ORMModel):
    value: Mapped[types.decimal_10_2]
    start_date: Mapped[types.moscow_datetime_timezone]
    end_date: Mapped[types.moscow_datetime_timezone] = mapped_column(
        default=dt.datetime(year=2099, month=1, day=1), nullable=True
    )

    bundle_variation_pod: Mapped[Optional[BundleVariationPodModel]] = relationship(
        back_populates="prices"
    )
