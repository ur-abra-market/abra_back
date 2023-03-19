from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core.types import category_id_fk


class CategoryIDMixin:
    category_id: Mapped[category_id_fk]
