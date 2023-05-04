from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..types import country_id_fk


class CountryIDMixin:
    country_id: Mapped[country_id_fk]
