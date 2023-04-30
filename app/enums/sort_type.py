from __future__ import annotations

from typing import Any

from aenum import MultiValueEnum

from orm import ProductModel, ProductPriceModel


class SortType(MultiValueEnum):
    RATING = "rating", ProductModel.grade_average.asc()
    PRICE = "price", ProductPriceModel.value.asc()
    DATE = "date", ProductModel.datetime.desc()
    TOTAL_ORDERS = "total_orders", ProductModel.total_orders.asc()

    @property
    def sort_type(self) -> Any:
        value, sort = self.values  # noqa
        return sort
