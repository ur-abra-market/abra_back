from __future__ import annotations

from .core import ORMSchema


class ProductImage(ORMSchema):
    image_url: str
    serial_number: int
