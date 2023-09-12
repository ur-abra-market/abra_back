from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import variation_value_fk
from ..types import variation_value_fk_type


class VariationValueIDMixin:
    variation_value_id: Mapped[variation_value_fk_type] = variation_value_fk
