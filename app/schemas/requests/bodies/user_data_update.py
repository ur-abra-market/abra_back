from __future__ import annotations

from typing import Optional

from ...mixins import PhoneNumber
from ...schema import ApplicationSchema


class UserDataUpdate(PhoneNumber, ApplicationSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
