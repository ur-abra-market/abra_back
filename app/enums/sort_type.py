from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar

from orm import ProductModel
from typing_ import DictStrAny


class SortType(Enum):
    ID = "id"
    RATING = "rating"
    PRICE = "price"
    DATE = "date"
    TOTAL_ORDERS = "total_orders"

    __table__: ClassVar[DictStrAny] = {
        ID: ProductModel.id,
        RATING: ProductModel.grade_average,
        #! PRICE: ProductPriceModel.value,
        DATE: ProductModel.created_at,
        TOTAL_ORDERS: ProductModel.total_orders,
    }

    @property
    def by(self) -> Any:
        return self.__table__.get(  # type: ignore[no-attr-defined]
            self.value,
            None,
        )
