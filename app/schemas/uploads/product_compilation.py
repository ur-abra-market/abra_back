from __future__ import annotations

from typing import Optional

from ..schema import ApplicationSchema


class ProductCompilationUpload(ApplicationSchema):
    category_id: Optional[int]
    ascending: bool = True
