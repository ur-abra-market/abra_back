from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..types import category_id_fk


class CategoryIDMixin:
    category_id: Mapped[category_id_fk]
