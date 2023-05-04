from __future__ import annotations

from typing import Optional

from ...schema import ApplicationSchema
from enums import CurrencyEmum


class SellerDeliveryData(ApplicationSchema): 
    currency: Optional[CurrencyEmum]
    country_id: Optional[int]