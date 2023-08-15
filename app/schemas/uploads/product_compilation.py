from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema


class ProductCompilationUpload(ApplicationSchema):
    category_ids: Optional[List[int]]
    ascending: bool = False
