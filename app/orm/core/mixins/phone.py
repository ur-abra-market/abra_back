from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from ..constraints import country_id_fk
from ..types import country_id_fk_type, str_14


class PhoneMixin:
    country_id: Mapped[Optional[country_id_fk_type]] = country_id_fk
    phone_number: Mapped[Optional[str_14]]
