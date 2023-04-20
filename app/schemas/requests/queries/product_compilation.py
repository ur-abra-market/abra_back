from __future__ import annotations

from typing import Any, List

from enums import SortType

from ...schema import ApplicationSchema


class ProductCompilation(ApplicationSchema):
    category_id: int = 0
    order_by: SortType = SortType.DATE

    def get_order_by(self) -> List[Any]:
        return [self.order_by.sort_type]
