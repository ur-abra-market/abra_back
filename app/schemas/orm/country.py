from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .seller_delivery import SellerDelivery


class Country(ORMSchema):
    country: str
    country_code: str
    flag: str
    deliveries: Optional[SellerDelivery] = None
