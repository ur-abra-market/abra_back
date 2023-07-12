from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .country import Country
    from .seller_address import SellerAddress


class SellerAddressPhone(ORMSchema):
    phone_number: Optional[str] = None
    seller_address: Optional[SellerAddress] = None
    country: Optional[Country] = None
