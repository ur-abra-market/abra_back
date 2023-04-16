from __future__ import annotations

from typing import Any, List, Optional

from enums import SortType

from ...schema import ApplicationSchema


class ProductCompilation(ApplicationSchema):
    category_id: int = 0
    order_by: Optional[SortType] = None

    def get_order_by(self) -> Optional[List[Any]]:
        if self.order_by and (sort_type := self.order_by.get_model_sort_type()) is not None:
            return [sort_type]
        return None
