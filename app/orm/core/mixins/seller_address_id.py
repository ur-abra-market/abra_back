from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..types import seller_address_fk


class SellerAddressIDMixin:
    seller_address_id: Mapped[seller_address_fk]
