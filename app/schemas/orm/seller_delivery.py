from __future__ import annotations

from typing import Optional

from .core import ORMSchema

from .seller import Seller
from .country import Country



class SellerDelivery(ORMSchema):
    seller: Optional[Seller] = None
    currency: str
    country: Optional[Country] = None