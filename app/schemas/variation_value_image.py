from __future__ import annotations

from .core import ORMSchema


class VariationValueImage(ORMSchema):
    variation_value_id: int
    image_url: str
    thumbnail_url: str
