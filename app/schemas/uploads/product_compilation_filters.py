from __future__ import annotations

from typing import List, Optional

from enums import ProductFilterValuesEnum

from ..schema import ApplicationSchema


class ProductListFiltersUpload(ApplicationSchema):
    category_ids: Optional[List[int]]
    on_sale: Optional[ProductFilterValuesEnum] = ProductFilterValuesEnum.ALL
