from __future__ import annotations

from ..schema import ApplicationSchema


class ProductImage(ApplicationSchema):
    image_url: str
    serial_number: int
