from enum import Enum


class OrderStatus(Enum):
    CART = 1
    UNPAID = 2
    SHIPPED = 3
    TO_BE_SHIPPED = 4
    TO_BE_REVIEWED = 5
    COMPLETED = 6
    PAID = 7
    AWAITING_REFUND = 8
    CANCELLED = 9
