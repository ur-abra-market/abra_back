from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .country import Country
    from .seller import Seller
    from .seller_address_phone import SellerAddressPhone


class SellerAddress(mixins.NameMixin, ORMSchema):
    is_main: bool = False
    area: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    postal_code: Optional[str] = None
    seller: Optional[Seller] = None
    country: Optional[Country] = None
    phone: Optional[SellerAddressPhone] = None
