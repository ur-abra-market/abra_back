from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from ..constraints import category_id_fk
from ..types import category_id_fk_type


class CategoryIDMixin:
    category_id: Mapped[category_id_fk_type] = category_id_fk


class ParentCategoryIDMixin:
    parent_id: Mapped[Optional[category_id_fk_type]] = category_id_fk
