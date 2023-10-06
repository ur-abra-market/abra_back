from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import country_id_fk
from ..types import country_id_fk_type


class CountryIDMixin:
    country_id: Mapped[country_id_fk_type] = country_id_fk
