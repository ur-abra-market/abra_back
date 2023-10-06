from __future__ import annotations

from ..schema import ApplicationSchema


class ProductIdUpload(ApplicationSchema):
    product_id: int
