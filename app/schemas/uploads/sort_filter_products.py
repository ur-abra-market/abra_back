from __future__ import annotations

from typing import Optional

from ..schema import ApplicationSchema


class SortFilterProductsUpload(ApplicationSchema):
    category_ids: Optional[list[int]]
    on_sale: Optional[bool]
    is_active: Optional[bool]
