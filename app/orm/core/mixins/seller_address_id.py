from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import seller_address_fk
from ..types import seller_address_fk_type


class SellerAddressIDMixin:
    seller_address_id: Mapped[seller_address_fk_type] = seller_address_fk
