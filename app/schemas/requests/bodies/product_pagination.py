from typing import List, Optional

from pydantic import BaseModel, Field

from ...schema import ApplicationSchema
from ._sort import Sort


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


class ProductPagination(_Variations, _Properties, _Price, Sort, ApplicationSchema):
    ...
