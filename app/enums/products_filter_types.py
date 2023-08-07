from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar

from orm import ProductModel
from typing_ import DictStrAny


class ProductsSortingTypesEnum(Enum):
    # PRICE = "price"
    DATE = "date"

    __table__: ClassVar[DictStrAny] = {
        DATE: ProductModel.datetime,
        # PRICE: ProductPriceModel.value,
    }

    @property
    def by(self) -> Any:
        return self.__table__.get(  # type: ignore[no-attr-defined]
            self.value,
            None,
        )
