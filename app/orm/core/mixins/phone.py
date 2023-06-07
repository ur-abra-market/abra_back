from __future__ import annotations

from typing import Any, Optional, Tuple

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped

from ..types import country_id_fk, str_14


class PhoneMixin:
    __table_args__: Tuple[Any, ...] = (
        CheckConstraint("char_length(phone_number) > 3", name="check_phone_number_length"),
    )

    country_id: Mapped[Optional[country_id_fk]]
    phone_number: Mapped[Optional[str_14]]
