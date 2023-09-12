from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import category_id_fk
from ..types import category_id_fk_type


class CategoryIDMixin:
    category_id: Mapped[category_id_fk_type] = category_id_fk


class ParentCategoryIDMixin:
    parent_id: Mapped[category_id_fk_type] = category_id_fk
