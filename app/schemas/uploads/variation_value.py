from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema


class VariationValueUpload(ApplicationSchema):
    variation_velues_id: int
    images: Optional[List[str]] = None
