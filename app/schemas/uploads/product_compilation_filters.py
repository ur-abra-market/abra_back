from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema


class ProductListFiltersUpload(ApplicationSchema):
    category_ids: Optional[List[int]]
    on_sale: Optional[bool]
