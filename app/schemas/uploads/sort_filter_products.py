from __future__ import annotations

from typing import Optional

from enums import ProductsSortingTypesEnum

from ..schema import ApplicationSchema


class SortFilterProductsUpload(ApplicationSchema):
    category_id: Optional[int]
    on_sale: Optional[bool]
    is_active: Optional[bool]
    sort: Optional[ProductsSortingTypesEnum]
    ascending: Optional[bool] = True
