from __future__ import annotations

from enums import OrderStatus as OrderStatusEnum

from ..schema import ApplicationSchema


class StatusDataUpload(ApplicationSchema):
    status_id: OrderStatusEnum = OrderStatusEnum.PENDING.value