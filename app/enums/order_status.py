from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    AWAITING_SHIPMENT = "awaiting_shipment"
    SHIPPED = "shipped"
    AWAITING_PICKUP = "awaiting_pickup"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    AWAITING_REFUND = "awaiting_refund"
