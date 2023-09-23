from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar

from orm import ProductModel
from typing_ import DictStrAny


class ProductsSortingTypesEnum(Enum):
    DATE = "date"
    PRICE = "price"
    RATING = "rating"

    __table__: ClassVar[DictStrAny] = {
        DATE: ProductModel.created_at,
        #! PRICE: ProductPriceModel.value,
        RATING: ProductModel.grade_average,
    }

    @property
    def by(self) -> Any:
        return self.__table__.get(  # type: ignore[no-attr-defined]
            self.value,
            None,
        )