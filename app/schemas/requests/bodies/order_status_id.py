from __future__ import annotations

from ...schema import ApplicationSchema


class OrderStatus(ApplicationSchema):
    status_id: int
