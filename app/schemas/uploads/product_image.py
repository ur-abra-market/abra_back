from __future__ import annotations

from ..schema import ApplicationSchema


class ProductImageUpload(ApplicationSchema):
    order: int
    image: str
