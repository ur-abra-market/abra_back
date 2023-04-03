from __future__ import annotations

from ...schema import ApplicationSchema


class PhoneNumber(ApplicationSchema):
    number: str
