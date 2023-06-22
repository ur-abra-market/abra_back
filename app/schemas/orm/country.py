from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from enums import CurrencyEnum

from .core import ORMSchema

if TYPE_CHECKING:
    from .seller_address import SellerAddress


class Country(ORMSchema):
    country: str
    country_code: str
    country_short: str
    currency: CurrencyEnum
    flag: str
    addresses: Optional[List[SellerAddress]] = None
