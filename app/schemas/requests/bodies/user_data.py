from __future__ import annotations

from typing import Optional

from ...schema import ApplicationSchema


class UserData(ApplicationSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
