from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import brand_id_fk
from ..types import brand_id_fk_type


class BrandIDMixin:
    brand_id: Mapped[brand_id_fk_type] = brand_id_fk
