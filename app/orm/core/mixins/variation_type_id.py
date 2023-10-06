from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import variation_type_fk
from ..types import variation_type_fk_type


class VariationTypeIDMixin:
    variation_type_id: Mapped[variation_type_fk_type] = variation_type_fk
