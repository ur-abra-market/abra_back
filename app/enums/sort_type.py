from enum import Enum
from typing import Any

from orm import ProductModel, ProductPriceModel

PRODUCT_SORTING_TYPES_MAP = {
    "rating": ProductModel.grade_average,
    "price": ProductPriceModel.value,
    "date": ProductModel.datetime.desc(),
    "total_orders": ProductModel.total_orders,
}


class SortType(Enum):
    RATING = "rating"
    PRICE = "price"
    DATE = "date"
    TOTAL_ORDERS = "total_orders"

    @property
    def sort_type(self) -> Any:
        return PRODUCT_SORTING_TYPES_MAP[self.value]
