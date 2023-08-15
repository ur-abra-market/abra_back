from __future__ import annotations

from typing import Optional

from ..schema import ApplicationSchema


class ProductCompilationUpload(ApplicationSchema):
    category_ids: Optional[int]
    ascending: bool = False
