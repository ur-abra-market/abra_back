from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..types import brand_id_fk


class BrandIDMixin:
    brand_id: Mapped[brand_id_fk]
