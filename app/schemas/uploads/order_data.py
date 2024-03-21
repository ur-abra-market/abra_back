from __future__ import annotations

from typing import Optional

from pydantic import Field

from enums import OrderStatus

from . import PaginationUpload


class OrderQueryParams(PaginationUpload):
    status: Optional[OrderStatus] = None
    query: Optional[str] = Field("", min_length=0)
