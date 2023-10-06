from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import seller_id_fk
from ..types import seller_id_fk_type


class SellerIDMixin:
    seller_id: Mapped[seller_id_fk_type] = seller_id_fk
