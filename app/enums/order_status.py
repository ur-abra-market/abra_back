from enum import Enum


class OrderStatus(str, Enum):
    PENDING = 1
    AWAITING_SHIPMENT = 2
    SHIPPED = 3
    AWAITING_PICKUP = 4
    COMPLETED = 5
    CANCELLED = 6
    AWAITING_REFUND = 7
