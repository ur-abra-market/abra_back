from enum import Enum


class OrderStatus(Enum):
    UNPAID = 1
    SHIPPED = 2
    TO_BE_SHIPPED = 3
    TO_BE_REVIEWED = 4
    COMPLETED = 5
    PAID = 6
    AWAITING_REFUND = 7
    CANCELLED = 8
