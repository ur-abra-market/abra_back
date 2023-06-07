from __future__ import annotations

from ...mixins import PhoneNumber
from ...schema import ApplicationSchema


class UserData(PhoneNumber, ApplicationSchema):
    first_name: str
    last_name: str
