from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema


class VariationValueUpload(ApplicationSchema):
    variation_type_id: int
    variation_values_images: Optional[List[str]] = None
