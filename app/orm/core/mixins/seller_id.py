from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core.types import seller_id_fk


class SellerIDMixin:
    seller_id: Mapped[seller_id_fk]
