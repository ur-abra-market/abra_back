from __future__ import annotations

from typing import Any, Optional, Tuple

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped

from ..types import str_14
from .country_id import CountryIDMixin


class PhoneMixin(CountryIDMixin):
    __table_args__: Tuple[Any, ...] = (
        CheckConstraint("char_length(phone_number) > 3", name="check_phone_number_length"),
    )

    phone_number: Mapped[Optional[str_14]]
