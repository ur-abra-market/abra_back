from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .seller import Seller


class SellerAddress(mixins.NameMixin, mixins.PhoneMixin, ORMSchema):
    is_main: bool = False
    country: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    postal_code: Optional[str] = None
    seller: Optional[Seller] = None
