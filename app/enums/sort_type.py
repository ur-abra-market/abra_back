from __future__ import annotations

from typing import Any

from aenum import MultiValueEnum

from orm import ProductModel, ProductPriceModel


class SortType(MultiValueEnum):
    ID = "id", ProductModel.id
    RATING = "rating", ProductModel.grade_average
    PRICE = "price", ProductPriceModel.value
    DATE = "date", ProductModel.datetime
    TOTAL_ORDERS = "total_orders", ProductModel.total_orders

    @property
    def by(self) -> Any:
        value, sort = self.values  # noqa
        return sort
