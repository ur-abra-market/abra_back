from __future__ import annotations

from .core import ORMSchema

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING: 
    from .seller_delivery import SellerDelivery


class Country(ORMSchema):
    country: str
    country_code: str
    flag: str
    delivery: Optional[SellerDelivery] = None
