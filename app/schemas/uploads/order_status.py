from __future__ import annotations

from ..schema import ApplicationSchema


class OrderStatusUpload(ApplicationSchema):
    status_id: int
