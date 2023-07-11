from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from enums import SortType

from ..schema import ApplicationSchema


class ProductPaginationUpload(ApplicationSchema):
    colors: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    materials: Optional[List[str]] = None
    age_groups: Optional[List[str]] = None
    genders: Optional[List[str]] = None
    technics: Optional[List[str]] = None
    min_price: Optional[int] = Field(None, alias="bottom_price")
    max_price: Optional[int] = Field(None, alias="top_price")
    with_discount: bool = False
    category_id: Optional[int] = None
    sort_type: SortType = SortType.RATING
    ascending: bool = False
