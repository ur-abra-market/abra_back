from enum import Enum


class OrderStatus(Enum):
    unpaid = 1
    shipped = 2
    to_be_shipped = 3
    to_be_reviwed = 4
    completed = 5
    paid = 6
    awaiting_a_refund = 7
    cancelled = 8
