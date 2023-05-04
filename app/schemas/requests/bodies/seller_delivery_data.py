from __future__ import annotations

from enums import CurrencyEnum

from ...schema import ApplicationSchema


class SellerDeliveryData(ApplicationSchema):
    currency: CurrencyEnum
    country_id: int
