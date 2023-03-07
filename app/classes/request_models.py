import datetime
from os import getenv
from typing import List, Optional, Any, Literal

from pydantic import BaseModel, validator

import app.logic.consts as constants
from app.settings import *


class RequestPagination(BaseModel):
    page_num: int = 1
    page_size: int = 10


class ProductsPaginationRequest(RequestPagination):
    """Input for data pagination."""

    category_id: Optional[int] = None
    bottom_price: Optional[int] = None
    top_price: Optional[int] = None
    with_discount: bool = False
    sort_type: str = "rating"
    ascending: bool = False
    sizes: Optional[List[str]] = None
    brands: Optional[List[str]] = None
    materials: Optional[List[str]] = None

    @validator("sort_type")
    def sort_validator(cls, v):
        assert v in constants.product_sort_types, "invalid sort_type"
        return v


class ProductsCompilationRequest(RequestPagination):
    order_by: constants.SortingTypes = None
    category_id: int = None
