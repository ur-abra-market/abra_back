from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import property_type_fk
from ..types import property_type_fk_type


class PropertyTypeIDMixin:
    property_type_id: Mapped[property_type_fk_type] = property_type_fk
