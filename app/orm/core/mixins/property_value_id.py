from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import property_value_fk
from ..types import property_value_fk_type


class PropertyValueIDMixin:
    property_value_id: Mapped[property_value_fk_type] = property_value_fk
