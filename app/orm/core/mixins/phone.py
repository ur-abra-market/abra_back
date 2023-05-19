from __future__ import annotations

from typing import Any, Optional, Tuple

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped

from ..types import str_4, str_14


class PhoneMixin:
    __table_args__: Tuple[Any, ...] = (
        CheckConstraint(
            "char_length(phone_country_code) > 0", name="check_phone_count_code_length"
        ),
        CheckConstraint("char_length(phone_number) > 3", name="check_phone_number_length"),
    )

    phone_country_code: Mapped[Optional[str_4]]  # with +
    phone_number: Mapped[Optional[str_14]]
