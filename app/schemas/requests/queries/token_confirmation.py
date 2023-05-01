from __future__ import annotations

from ...schema import ApplicationSchema


class TokenConfirmation(ApplicationSchema):
    token: str
