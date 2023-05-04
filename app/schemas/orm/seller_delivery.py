from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from enums import CurrencyEnum

from .core import ORMSchema

if TYPE_CHECKING:
    from .country import Country
    from .seller import Seller


class SellerDelivery(ORMSchema):
    currency: CurrencyEnum
    seller: Optional[Seller] = None
    country: Optional[Country] = None
