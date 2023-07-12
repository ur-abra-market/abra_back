from __future__ import annotations

from typing import Optional

from enums import SortType

from ..schema import ApplicationSchema


class ProductCompilationUpload(ApplicationSchema):
    category_id: Optional[int] = None
    sort_type: SortType = SortType.RATING
    ascending: bool = False
