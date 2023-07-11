from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from enums import SortType

from .schema import ApplicationSchema


class _Variations(BaseModel):
    colors: Optional[List[str]] = None
    sizes: Optional[List[str]] = None


class _Properties(BaseModel):
    materials: Optional[List[str]] = None
    age_groups: Optional[List[str]] = None
    genders: Optional[List[str]] = None
    technics: Optional[List[str]] = None


class _Price(BaseModel):
    min_price: Optional[int] = Field(None, alias="bottom_price")
    max_price: Optional[int] = Field(None, alias="top_price")
    with_discount: bool = False


class ProductPaginationUpload(_Variations, _Properties, _Price, ApplicationSchema):
    category_id: Optional[int] = None
    sort_type: SortType = SortType.RATING
    ascending: bool = False
